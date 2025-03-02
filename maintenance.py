import rdm6300
import os
import subprocess

def stopService():
    os.system("sudo systemctl stop rdm6300.service")
    # check if service was stopped
    result = subprocess.run(["systemctl", "is-active", "rdm6300.service"], stdout=subprocess.PIPE)
    if "inactive" in result.stdout.decode("utf-8"):
        print("__main service stopped, continuing__\n")
    else:
        print("###############################################\n__main service error in stopping__\n- sudo systemctl stop rdm6300.service\n- sudo systemctl status rdm6300.service")
        exit()

def startService():
    os.system("sudo systemctl start rdm6300.service")
    # check if service was started
    result = subprocess.run(["systemctl", "is-active", "rdm6300.service"], stdout=subprocess.PIPE)
    if "active" in result.stdout.decode("utf-8") and "inactive" not in result.stdout.decode("utf-8"):
        print("\n__main service restarted__\n")
    else:
        print("\n###############################################\n__main service error in restarting__\n- sudo systemctl start rdm6300.service\n- sudo systemctl status rdm6300.service")
        exit()

def restartService():
    os.system("sudo systemctl restart rdm6300.service")
    # check if service was restarted
    result = subprocess.run(["systemctl", "is-active", "rdm6300.service"], stdout=subprocess.PIPE)
    if "active" in result.stdout.decode("utf-8") and "inactive" not in result.stdout.decode("utf-8"):
        print("\n__main service restarted__\n")
    else:
        print("\n###############################################\n__main service error in restarting__\n- sudo systemctl restart rdm6300.service\n- sudo systemctl status rdm6300.service")
        exit()

def checkDuplicateTagInFile(tag):
    with open("tags.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if str(tag) in line:
                # return indexTag
                return line.split(" ")[1]
    return False

class Reader(rdm6300.BaseReader):
    def card_inserted(self, card):
        print(f"card inserted {card}")
        checkDupe = checkDuplicateTagInFile(card.value)
        if checkDupe != False:
            print(f"Tag {card.value} ", end="")
            print('\x1b[6;30;41m' + "ALREADY EXISTS" + '\x1b[0m', end="")
            print(f" in tags.txt with index {checkDupe}")
            r.close()
            r.stop()
            return
        
        with open("tags.txt", "a") as file:
            # file.write(f"{indexTag} {card.value}\n")
            file.write(f"{card.value} {indexTag}\n")
        print(f"Tag {card.value} with index {indexTag} added to tags.txt")
        r.close()
        r.stop()

    def card_removed(self, card):
        print(f"card removed {card}")

    def invalid_card(self, card):
        print(f"invalid card {card}")

def listTags():
    print('\nIndex\tTag\n===================')
    with open("tags.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            print(f'{line.strip().split(" ")[1]}\t{line.strip().split(" ")[0]}')

# MAIN
stopService()

print('Choose an option:')
print('1. Restart service')
print('2. Add new tag')
print('3. List tags')
print('4. Remove tag')
print('0. Exit')
inputOption = input('Option: ')
if inputOption == "1":
    restartService()
elif inputOption == "3":
    listTags()
elif inputOption == "4":
    listTags()
    indexTag = input("Enter the index of the tag to remove: ")
    try:
        indexTag = int(indexTag)
    except:
        print("Invalid input")
        exit()
    with open("tags.txt", "r") as file:
        lines = file.readlines()
    tagFound = False
    with open("tags.txt", "w") as file:
        for line in lines:
            if indexTag != int(line.split(" ")[1]):
                file.write(line)
            else:
                tagFound = True
    if tagFound:
        print(f"Tag with index {indexTag} removed")
    else:
        print(f"Tag with index {indexTag} not found")
elif inputOption == "0":
    exit()
elif inputOption == "2":










    # restart service on errors











    # if file does not exist, create it
    try:
        file = open("tags.txt", "r")
        file.close()
    except:
        file = open("tags.txt", "w")
        file.close()

    indexTag = input("Enter the index of the tag: ")
    try:
        indexTag = int(indexTag)
    except:
        print("Invalid input")
        exit()

    print("Insert the tag")
    # Find USB device (in case of reconnect)
    import subprocess
    result = subprocess.run(["find", "/dev", "-name", "ttyUSB*"], stdout=subprocess.PIPE)
    listUSB = result.stdout.decode("utf-8").split("\n")
    listUSB.pop()
    print(listUSB)

    if len(listUSB) == 0:
        raise Exception("No USB device found")

    # r = Reader('/dev/ttyUSB0')
    r = Reader(listUSB[0])
    r.start()

    # sort tags.txt by index
    with open("tags.txt", "r") as file:
        lines = file.readlines()
        lines.sort(key=lambda x: int(x.split(" ")[1]))
    with open("tags.txt", "w") as file:
        for line in lines:
            file.write(line)

else:
    print("Invalid input")
    exit()

startService()