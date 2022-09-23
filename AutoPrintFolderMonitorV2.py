import os
import subprocess
import datetime

logFolderPath = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs"

# powershell command to get a list of files between 3 and 6 minutes old. 
listOfFilesCommand = r"Get-ChildItem -Path \\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs | Where-Object {$_.LastWriteTime -gt (Get-Date).AddMinutes(-6) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-3)} | select Name"

fileList = subprocess.run(["powershell", "-Command", listOfFilesCommand], text=True, capture_output=True).stdout.strip().splitlines() 

# clean the data by removing the first 2 items of the list
del(fileList[0:2])
print (fileList)

for fileName in fileList:
    
    fullFilePath = os.path.join(logFolderPath, fileName)
    print(f"testing - {fileName}")

    # Open the file
    with open(fullFilePath, 'r') as f:
        readLines = f.readlines()
        # Set counter up to be able to read through each line
        counter = 0
        for line in readLines:
            # Find Copying in the line
            if "Copying" in line:
                time1 = readLines[counter][0:19]
                time1Object = datetime.strptime(time1, "%m/%d/%Y %H:%M:%S")
                print("Found the word - Copying")
                # Make sure the line after "copying" exists
                try:
                    time2 = readLines[counter+1][0:19]
                
                # if the line after does not exist, add to workingFileDict and check later
                except: 
                    # add the event and timestamp to workingFileDict so that it can be checked later
                    print('Next Line does not exist')
                    print(readLines[0].strip())
                    # restart trulinx com service
                    # print("restarting trulinx com app")
                    # restartCommand = subprocess.run(["powershell", "-Command", restartTrulinxComApp], capture_output=True)
                    # print (restartCommand.stdout.splitlines())
                    print("Sending email")
                    # Send Email
                    sendEmail(message = f"Failed Auto Print \n\n\n{docTime} - {keyList[i]} \n\nTotal items\n {list(workingFileDict.keys())}", subject = "Failed Auto Print", emailTo = "cstogsdill@midwesthose.com", emailFrom = "chris1stogsdill@gmail.com")
                    break    
            # Increment counter for the next loop.
            counter += 1

        # Close the file 
        f.close()