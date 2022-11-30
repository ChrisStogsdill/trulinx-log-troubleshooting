import datetime
with open("./logs/test.txt", "a") as log:
    today = datetime.date.today()
    today = today.strftime("%Y%m%d")
    log.write(today + "\n")
    print(datetime.datetime.now())