from machine import Pin
import time

led = Pin("LED", Pin.OUT)   # on‑board LED

while True:
    led.toggle()
    time.sleep(0.5)