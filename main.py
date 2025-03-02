import rdm6300

import threading
import time
import RPi.GPIO as GPIO

from config import dictNrUsaToGPIO, pinBuzzer, timeDoorOpen

def threadBuzzer(count=2, duration=0.1):
    def beep():
        for _ in range(count):
            GPIO.output(pinBuzzer, GPIO.LOW)
            time.sleep(duration)
            GPIO.output(pinBuzzer, GPIO.HIGH)
            time.sleep(0.06)
    
    threading.Thread(target=beep).start()

dictTagToNrUsa = {} # {"7092123": 1, "3411724": 2, ...} Read from tags.txt
timeLastCard = time.time() # prevent multiple card reads in short time

with open("tags.txt", "r") as file:
    for line in file:
        tag = int(line.split(" ")[0].strip())
        nrUsa = int(line.split(" ")[1].strip())
        dictTagToNrUsa[tag] = nrUsa

class Reader(rdm6300.BaseReader):
    def card_inserted(self, card):
        print(f"card inserted {card}")

        global timeLastCard

        if time.time() - timeLastCard < 1:
            threadBuzzer(1, 0.7)
            return

        if card.value in dictTagToNrUsa:
            if dictTagToNrUsa[card.value] in dictNrUsaToGPIO:
                GPIO.output(dictNrUsaToGPIO[dictTagToNrUsa[card.value]], GPIO.LOW)
                threadBuzzer()
                time.sleep(timeDoorOpen)
                GPIO.output(dictNrUsaToGPIO[dictTagToNrUsa[card.value]], GPIO.HIGH)
                threadBuzzer(1, 0.1)
            elif dictTagToNrUsa[card.value] == 0: # MASTER CARD
                threadBuzzer(count=4)
                for pin in dictNrUsaToGPIO.values():
                    GPIO.output(pin, GPIO.LOW)
                    time.sleep(0.1)
                time.sleep(timeDoorOpen)
                for pin in dictNrUsaToGPIO.values():
                    GPIO.output(pin, GPIO.HIGH)
                    time.sleep(0.1)
                threadBuzzer(1, 0.1)
            else:
                print(f"Tag {card.value} has no corresponding GPIO")
                threadBuzzer(3, 0.7)
        else:
            print(f"Tag {card.value} not found in tags.txt")
            threadBuzzer(2, 0.7)

        timeLastCard = time.time()

    def card_removed(self, card):
        print(f"card removed {card}")

    def invalid_card(self, card):
        print(f"invalid card {card}")
        threadBuzzer(4, 0.7)

GPIO.setmode(GPIO.BCM)

GPIO.setup(pinBuzzer, GPIO.OUT, initial=GPIO.HIGH)
for pin in dictNrUsaToGPIO.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

# Startup sound
threadBuzzer(1, 0.3)
time.sleep(0.4)
threadBuzzer(3, 0.1)

try:
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
except Exception as e:
    # telegram message ???
    print(e)
    time.sleep(3)
    for _ in range(3):
        threadBuzzer(1, 0.7)
        time.sleep(1.5)
    GPIO.cleanup()
    exit()
