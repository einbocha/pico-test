import network, uasyncio as asyncio
import time
import ujson
import urequests
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# I2C setup (default pins GP4=SDA, GP5=SCL for Pico I2C0)
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
oled = SSD1306_I2C(128, 32, i2c)
# Scan and print I2C devices (should show 0x3C)
# print('I2C devices:', [hex(addr) for addr in i2c.scan()])

SSID = ""
PASSWORD = ''
STATE = '/state.json'
AUTH_NAME = ''
AUTH_PWD = ''
SERVER_URL = ''

WEB_PORT = 80

# Wi-Fi connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def write_state(state):
    try:
        with open(STATE, 'w') as f:
            f.write(ujson.dumps(state))

        print(f'Saved state')
    except Exception as e:
        print('Write error:', e)


def read_state():
    try:
        with open(STATE, 'r') as f:
            return ujson.loads(f.read())
    except Exception as e:
        print('Read error:', e)
        return None


if not read_state():
    write_state({
        'state': [],
    })


async def connect_wifi():
    while True:
        if not wlan.isconnected():
            print('WiFi: Disconnected - reconnecting...')

            try:
                wlan.connect(SSID, PASSWORD)

                # Non-blocking connection check with timeout
                timeout = 20  # 20 seconds max
                while not wlan.isconnected() and timeout > 0:
                    await asyncio.sleep(1)
                    timeout -= 1
                    print('.', end='')

                if wlan.isconnected():
                    ip = wlan.ifconfig()[0]
                    print(f'\n✓ WiFi connected! IP: {ip}')
                else:
                    print('\n✗ WiFi timeout - retrying...')
                    wlan.disconnect()

            except Exception as e:
                print(f'WiFi error: {e}')

        # in both cases: already connected and timeout - do we retry after long pause
        await asyncio.sleep(30)


async def personal_state():
    while True:
        if wlan.isconnected():
            try:
                response = urequests.get(
                    SERVER_URL,
                    auth=(AUTH_NAME, AUTH_PWD)
                )

                data = ujson.loads(response.text)

                print(data)

                write_state(data)

                response.close()

            except Exception as e:
                print('HTTP error:', e)

            await asyncio.sleep(21)


async def display_state():
    # state check could append some log msg to the state if bad (no wifi etc)
    while True:
        state = read_state()

        messages = state['state']

        wifi_status = f'http://{wlan.ifconfig()[0]}:{WEB_PORT}' if wlan.isconnected() else 'offline'

        messages.append(wifi_status)

        old = ''
        for msg in messages:
            if len(msg) > 16:
                old = msg[:16]
                msg = msg[16:]
            oled.fill(0)
            oled.text(old, 0, 0)
            oled.text(msg, 0, 20)
            oled.show()
            old = msg
            await asyncio.sleep(5)


html = """\
HTTP/1.0 200 OK\r
Content-Type: text/html\r
\r
<!DOCTYPE html>
<html><body><h1>Hello from Pico W</h1></body></html>
"""

async def handle_client(reader, writer):
    try:
        request = await reader.read(1024)
        await writer.awrite(html.encode())
    finally:
        await writer.aclose()


async def main():
    asyncio.create_task(connect_wifi())
    asyncio.create_task(personal_state())
    asyncio.create_task(display_state())

    # Start server LAST
    server = await asyncio.start_server(handle_client, "0.0.0.0", WEB_PORT)

    while True:
        await asyncio.sleep(1)


asyncio.run(main())
