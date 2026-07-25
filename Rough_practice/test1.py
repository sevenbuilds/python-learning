from datetime import datetime
from time import sleep

current_time = datetime.now().strftime("%I:%M:%S")
print(current_time)
given_time = input("what time?")

while True:
    current_time = datetime.now().strftime("%I:%M:%S")
    print(current_time)
    if current_time >= given_time:
        print("that time reached")
        break
    sleep(1)


