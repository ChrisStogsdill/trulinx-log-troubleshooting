import os
from datetime import datetime

tempLogsDir = r"C:\Users\cstogsdill\Downloads\temp logs"
users = []
for file in os.listdir(tempLogsDir):
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
    f.close()


