import os
import subprocess

# powershell command to get a list of files between 3 and 6 minutes old. 
listOfFilesCommand = r"Get-ChildItem -Path \\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs | Where-Object {$_.LastWriteTime -gt (Get-Date).AddMinutes(-6) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-3)} | select Name"

fileList = subprocess.run(["powershell", "-Command", listOfFilesCommand], text=True, capture_output=True).stdout.strip().splitlines() 

# clean the data by removing the first 2 items of the list
del(fileList[0:2])
print (fileList)

try: 
    # Open the file
    with open(event.src_path, 'r') as f:
        readLines = f.readlines()
        # Set counter up to be able to read through each line
        counter = 0
        for line in readLines:
            # Find Copying in the line
            if "Copying" in line:
                time1 = readLines[counter][0:19]
                time1Object = datetime.strptime(time1, "%m/%d/%Y %H:%M:%S")

                # Make sure the line after "copying" exists
                try:
                    time2 = readLines[counter+1][0:19]
                
                # if the line after does not exist, add to workingFileDict and check later
                except: 
                    # add the event and timestamp to workingFileDict so that it can be checked later

                    workingFileDict.update({event.src_path: time1Object})

                    
                    print('Potential issue detected - WorkingFileDict updated')
                    print(readLines[0].strip())
                    
                    continue    
            # Increment counter for the next loop.
            counter += 1

        # Close the file 
        f.close()

    # check the status of each item in workingFileDict
    keyList = list(workingFileDict.keys())
    for i in range(len(keyList)):
        currentTime = datetime.now()
        docTime = workingFileDict[keyList[i]]
        timeDifference = currentTime - docTime
        if (timeDifference.seconds > 180) :
            print(currentTime - docTime)
            with open(keyList[i], "r") as file:
                lines = file.readlines()
                lineCounter = 0
                for line in lines:
                    if "Copying" in line :
                        try:
                            print(f"testing - {keyList[i]}")
                            testLine = lines[lineCounter+1]
                            # if testLine does not throw an error, then clear out the entry
                            workingFileDict.pop(keyList[i])
                            print("File printed successfully - removing from WorkingFileDict")
                            # if TestLine fails, send the email
                        except: 
                            # restart trulinx com service
                            # print("restarting trulinx com app")
                            # restartCommand = subprocess.run(["powershell", "-Command", restartTrulinxComApp], capture_output=True)
                            # print (restartCommand.stdout.splitlines())
                            print("Test Failed - Sending email")
                            # Send Email
                            sendEmail(message = f"Failed Auto Print \n\n\n{docTime} - {keyList[i]} \n\nTotal items\n {list(workingFileDict.keys())}", subject = "Failed Auto Print", emailTo = "cstogsdill@midwesthose.com", emailFrom = "chris1stogsdill@gmail.com")
                            workingFileDict.clear()

                    lineCounter += 1
                file.close()                 
            
                
        
except Exception as e: 
    print(e)
            