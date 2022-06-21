import os
from datetime import datetime

tempLogsDir = r"C:\Users\cstogsdill\Downloads\temp logs"

for file in os.listdir(tempLogsDir):
    with open(os.path.join(tempLogsDir, file), 'r') as f:
        readLines = f.readlines()
        counter = 0
        if 'No match found in system-defined printers.' in readLines[3]:
            print(readLines[0].strip('\n\r'))
            print(readLines[2].strip('\n\r'))
            print(readLines[3])
    f.close()


