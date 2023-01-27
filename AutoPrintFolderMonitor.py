import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
from sendEmailFromSupport import sendEmail

workingFileDict = {}
now = datetime.datetime.now()


def log(input):
    # get today as datetime
    today = datetime.date.today().strftime("%Y%m%d")
    # convert today as string
    # today = today.strftime("%Y%m%d")

    logFile = f"./logs/{today}-PrintMonitor.log"
    with open(logFile, "a") as file:
        file.write(str(input) + "\n")

log(f"{now} - starting script")


# powershell command to run on Trulinx server
# This doesn't need to be here anymore. mainly keeping it here to make sure the script is still running
# and to be an example of running a command on a server
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
# text for restarting the trulinx com service
restartTrulinxComApp = r"""
Invoke-Command -ComputerName corp-app-11 -ScriptBlock {
    $comAdmin = New-Object -com ("COMAdmin.COMAdminCatalog.1")
    $comAdmin.ShutdownApplication("TrulinX")
    $comAdmin.StartApplication("TrulinX")
}
"""

# this both serves to test the subprocess but also makes sure powershell is prepared for it.
testOutput = subprocess.run(["powershell", "-Command", listComApps], capture_output=True)
log("list of services")
log(testOutput.stdout.decode("utf-8"))

# Setting up the folder watch class
class OnMyWatch:
    # Set the directory on watch
    watchDirectory = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs"
    # watchDirectory = r"C:\Users\cstogsdill\Downloads\temp logs"
  
    # initialize the class with the observer method
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        startTime = datetime.datetime.now()
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = False)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
                timeRunning = datetime.datetime.now() - startTime
                # check how long this has been running. Stop after Time in seconds. Should be 18000
                if timeRunning.seconds > 18000:
                    log("time limit reached. Stopping observer")
                    self.observer.stop()
                    log("Stopped")
                    return "Stopped"
        except Exception as e:
            self.observer.stop()

            log("Observer Stopped")
            log(str(e))
  
        self.observer.join()
  
  
class Handler(FileSystemEventHandler):
  
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            # Event is created, you can process it now
            currentTime = time.strftime("%Y-%m-%d %H:%M:%S")
            # sleep for 10 seconds to try and cut down on false positives.
            time.sleep(10)

            log(f"{currentTime} - Created File event - {event.src_path}")

            # sometimes the file just doesn't exist anymore. wrapping in a try statement
            # in order to not fail out the whole program when that happens
            try: 
                # Open the file
                with open(event.src_path, 'r') as f:
                    readLines = f.readlines()

                    # check for bad printer setup
                    if 'No match found in system-defined printers.' in readLines[3]:
                        log("bad printer setup detected")
                        log(readLines[0].strip('\n\r'))
                        log(readLines[2].strip('\n\r'))
                        log(readLines[3].strip('\n\r'))

                        # send email about bad printer
                        sendEmail(message = f"Bad Printer Detected \n\n{event.src_path}\n\n{readLines[0]}{readLines[2]}{readLines[3]}", subject = "Bad Printer Setup", emailTo = "jferguson@midwesthose.com", emailFrom = "mwhsupport@midwesthose.com")

                        log("email sent")


                    # Set counter up to be able to read through each line
                    counter = 0
                    for line in readLines:
                        # Find "Getting data for the report" in the line
                        if "Getting data for the report" in line:
                            time1 = readLines[counter][0:19]
                            time1Object = datetime.datetime.strptime(time1, "%m/%d/%Y %H:%M:%S")

                            # Make sure 2 lines after "Getting data for the report" exists
                            # this catches both types of print jobs
                            try:
                                time2 = readLines[counter+2][0:19]
                            
                            # if the line after does not exist, then an email needs to be sent
                            except: 
                                # add the event and timestamp to workingFileDict so that it can be checked later

                                workingFileDict.update({event.src_path: time1Object})

                                
                                log('Potential issue detected - WorkingFileDict updated')
                                log(readLines[0].strip())
                                                                
                                continue    
                        # Increment counter for the next loop.
                        counter += 1



                # check the status of each item in workingFileDict
                keyList = list(workingFileDict.keys())
                for i in range(len(keyList)):
                    currentTime = datetime.datetime.now()
                    docTime = workingFileDict[keyList[i]]
                    timeDifference = currentTime - docTime
                    if (timeDifference.seconds > 180) :
                        log(currentTime - docTime)
                        with open(keyList[i], "r") as file:
                            lines = file.readlines()
                            lineCounter = 0
                            for line in lines:
                                if "Getting data for the report" in line :
                                    try:
                                        log(f"testing - {keyList[i]}")
                                        # test if 2 lines after "getting data for the report" exist
                                        # it will trigger an error if it does not
                                        testLine = lines[lineCounter+2]

                                        # get total print time for document
                                        docStartTime = lines[0][0:19]
                                        startTimeObject = datetime.datetime.strptime(docStartTime, "%m/%d/%Y %H:%M:%S")
                                        docEndTime = lines[-1][0:19]
                                        endTimeObject = datetime.datetime.strptime(docEndTime, "%m/%d/%Y %H:%M:%S")
                                        totalTime = endTimeObject - startTimeObject

                                        log(f"Total print time: {totalTime}")

                                        # if testLine does not throw an error, then clear out the entry
                                        workingFileDict.pop(keyList[i])
                                        log("File printed successfully - removing from WorkingFileDict")
                                        # if TestLine fails, send the email
                                    except Exception as e:
                                        log(str(e))
                                        # restart trulinx com service
                                        log("restarting trulinx com app")
                                        restartCommand = subprocess.run(["powershell", "-Command", restartTrulinxComApp], capture_output=True)
                                        log(restartCommand.stdout.decode('utf-8'))
                                        log("Test Failed - Sending email")
                                        # Send Email
                                        sendEmail(message = f"Failed Auto Print \n\nTrulinx Service Restarted\n\n{docTime} - \n{keyList[i]} \n\nTotal items\n {', '.join(keyList)}", subject = "Failed Auto Print", emailTo = "cstogsdill@midwesthose.com", emailFrom = "mwhsupport@midwesthose.com")
                                        workingFileDict.clear()

                                lineCounter += 1
             
                        
                            
                    
            except Exception as e: 
                log(str(e))
            
        # elif event.event_type == 'modified':
            # Event is modified, you can process it now
            # log("Watchdog received modified event - % s." % event.src_path)

watch = OnMyWatch()
watch.run()
