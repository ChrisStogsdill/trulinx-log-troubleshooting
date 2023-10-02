import os
from datetime import datetime

tempLogsDir = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs"
users = []
currentTime = datetime.now()
for file in os.listdir(tempLogsDir):
    filePath = os.path.join(tempLogsDir, file)
    fileTime = datetime.fromtimestamp(os.path.getmtime(filePath))
    fileAge = currentTime - fileTime

    with open(os.path.join(tempLogsDir, file), 'r') as f:
        readLines = f.readlines()
        counter = 0
        searchString  = 'No match found in system-defined printers.'

        # Loop through readLines to find the line with the searchString
        for line in readLines:
            if searchString in line:
                if tempUserList[-1] not in users:
                    users.append(tempUserList[-1])
                    print(readLines[0].strip('\n\r'))
                    print(readLines[2].strip('\n\r'))
                    print(readLines[3])
                    continue



