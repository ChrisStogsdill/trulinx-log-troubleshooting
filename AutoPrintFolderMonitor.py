import sys
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from datetime import datetime
from sendEmail import sendEmail



# powershell command to run on Trulinx server
listComApps = r"""
Invoke-Command -ComputerName corp-app-11 -ScriptBlock {
    $comAdmin = New-Object -com ("COMAdmin.COMAdminCatalog.1")
    $applications = $comAdmin.GetCollection("Applications") 
    $applications.Populate() 

    foreach ($application in $applications)
    {
    Write-Host $application.Name
    }

}
"""

testOutput = subprocess.run(["powershell", "-Command", listComApps], capture_output=True)
print (testOutput.stdout.splitlines())

class OnMyWatch:
    # Set the directory on watch
    watchDirectory = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs"
  
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Observer Stopped")
  
        self.observer.join()
  
  
class Handler(FileSystemEventHandler):
  
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            # Event is created, you can process it now

            # sleep for 3 minutes to try and cut down on false positives.
            time.sleep(180)
            # print("Watchdog received created event - % s." % event.src_path)
            with open(event.src_path, 'r') as f:
                readLines = f.readlines()
                counter = 0
                for line in readLines:
                    
                    if "Copying" in line:
                        time1 = readLines[counter][0:19]
                        time1Object = datetime.strptime(time1, "%m/%d/%Y %H:%M:%S")

                        # sometimes the line after Copying does not exist. 
                        # Need to continue the loop when that happens
                        try:
                            time2 = readLines[counter+1][0:19]
                        except: 
                            emailBody = f"""Failed Auto Print \n{time1Object} - {event.src_path}"""
                            emailSubject = "Failed Auto Print"

                            print('DID NOT PRINT')
                            print(readLines[0].strip())
                            print(f"{time1Object} - {event.src_path} \n")
                            sendEmail(message = emailBody, subject = emailSubject, emailTo = "cstogsdill@midwesthose.com", emailFrom = "chris1stogsdill@gmail.com")
                            continue
                        
                    counter += 1
            f.close()
        # elif event.event_type == 'modified':
            # Event is modified, you can process it now
            # print("Watchdog received modified event - % s." % event.src_path)

watch = OnMyWatch()
watch.run()
