import os
from datetime import datetime

tempLogsDir = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs"
users = []
currentTime = datetime.now()
for file in os.listdir(tempLogsDir):
    filePath = os.path.join(tempLogsDir, file)
    fileTime = datetime.fromtimestamp(os.path.getmtime(filePath))
    fileAge = currentTime - fileTime

    # see if file is within 7 days old
    if fileAge.days < 7:
        with open(os.path.join(tempLogsDir, file), 'r') as f:
            readLines = f.readlines()
            counter = 0
            
            if 'No match found in system-defined printers.' in readLines[3]:
                tempUserList = readLines[0].split(' ')
                if tempUserList[-1] not in users:
                    users.append(tempUserList[-1])
                    print(readLines[0].strip('\n\r'))
                    print(readLines[2].strip('\n\r'))
                    print(readLines[3])



