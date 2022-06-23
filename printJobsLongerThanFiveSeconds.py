import os
from datetime import datetime

tempLogsDir = r"C:\Users\cstogsdill\Downloads\temp logs"

for file in os.listdir(tempLogsDir):
    with open(os.path.join(tempLogsDir, file), 'r') as f:
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
                    continue

                time2Object = datetime.strptime(time2, "%m/%d/%Y %H:%M:%S")
                totalTime = time2Object - time1Object
                if totalTime.seconds > 5:
                    print (readLines[0].strip('\n\r'))
                    if "Counter Order" in readLines[25]:
                        print (readLines[25].strip('\n\r'))
                    print(readLines[counter].strip('\n\r'))
                    print(readLines[counter+1].strip('\n\r'))
                    print('time to copy ',totalTime , '\n')
                    
                
            counter += 1
    f.close()
