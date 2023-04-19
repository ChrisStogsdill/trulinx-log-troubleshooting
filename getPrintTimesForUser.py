import os
from datetime import datetime

tempLogsDir = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs"
counter = 0
longPrintCounter = 0
for file in os.listdir(tempLogsDir):
    with open(os.path.join(tempLogsDir, file), 'r') as f:
        readLines = f.readlines()

        userName = 'OKCCOUNTER'
        if userName in readLines[0]:
            print(f"Testing doc {file}")
            docStartTime = readLines[0][0:19]
            startTimeObject = datetime.strptime(docStartTime, "%m/%d/%Y %H:%M:%S")
            docEndTime = readLines[-1][0:19]
            endTimeObject = datetime.strptime(docEndTime, "%m/%d/%Y %H:%M:%S")
            totalTime = endTimeObject - startTimeObject
            print(readLines[0].strip())
            if 'Counter Order' in readLines[25]:
                print(readLines[25].strip('\n\r'))
            print("Total time (seconds): " + str(totalTime.seconds) + '\n')
            counter += 1
            if totalTime.seconds > 10:
                longPrintCounter += 1  
    f.close()
print('total jobs: ' + str(counter))
print('jobs over 10 seconds: ' + str(longPrintCounter))