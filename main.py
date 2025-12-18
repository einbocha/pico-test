import network, uasyncio as asyncio, socket
import time

SSID = "einbocha's iPhone"
PASSWORD = "bfowcueldicnejlvevxkg"

# Wi-Fi connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(SSID, PASSWORD)

print('Connecting to', SSID)
while not wlan.isconnected():
    time.sleep(1)
    print('.', end='')

print("\nIP:", wlan.ifconfig()[0])

html = """\
HTTP/1.0 200 OK\r
Content-Type: text/html\r
\r
<!DOCTYPE html>
<html>
<body>
<h1>Pico Form</h1>
<form method="POST" action="/">
<label>LED:</label>
<select name="led">
<option value="on">On</option>
<option value="off">Off</option>
</select>
<button type="submit">Send</button>
</form>
</body>
</html>
"""


async def handle_client(reader, writer):
    try:
        request = await reader.read(1024)
        req = request.decode()
        req = req.split('\n')

        for line in req:
            print(line + '\n')
        await writer.awrite(html)
    finally:
        await writer.aclose()

async def main():
    # Manual server loop instead of server.serve_forever()
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Server running on port 80")
    while True:
        # On some builds simply keeping the event loop alive is enough;
        # the server internally accepts connections.
        await asyncio.sleep(1)

asyncio.run(main())
