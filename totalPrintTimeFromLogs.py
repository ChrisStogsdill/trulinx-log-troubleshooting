import os
from datetime import datetime
counter = 0
totalCount = 0
badPrints = []

tempLogsDir = r"\\corp-app-11\c$\Users\trbadm\AppData\Local\TrulinX\ReportRunnerLogs - Backup"

for file in os.listdir(tempLogsDir):
    totalCount += 1
    with open(os.path.join(tempLogsDir, file), 'r') as f:
        readLines = f.readlines()
        time1 = readLines[0][0:19]
        time1Object = datetime.strptime(time1, "%m/%d/%Y %H:%M:%S")

        time2 = readLines[-1][0:19]
        try:
            time2Object = datetime.strptime(time2, "%m/%d/%Y %H:%M:%S")
        except:
            print("Bad Print detected")
            print(readLines[-1])
            print("")
            badPrints.append(file)
            continue

        

        totalTime = time2Object - time1Object
        
        if totalTime.seconds > 30:
            print(file)
            print(readLines[5])
            print (readLines[0].strip('\n\r'))
            if "Counter Order" in readLines[25]:
                print (readLines[25].strip('\n\r'))

            print('time to print ',totalTime , '\n\n')

            counter += 1
        


    f.close()
print("total prints longer than 30 seconds: ", counter, "\n")
print("total prints: ", totalCount , "\n")
print("bad prints: ", badPrints)
