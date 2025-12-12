# Copying / running code on the pico
1. Make sure you'r in your python environment (venv activated).
2. Make sure mpremote is installed (via pip install mpremote).
3. copy file to raspberry pi pico: mpremote cp main.py :main.py
4. start the script: mpremote reset

# Connecting to the python repl
1. Connect the raspberry pi without pressing the button (its only for firmware flashing)
2. make sure nothing runs currently by running i.e.: mpremote ls
2. mpremote repl
3. (alternative to the 2.:) screen /dev/tty.usbmodem1101 115200
2. exit with control-a-k and the press 'y' to confirm

# Flash / install any packages, drivers, libraries or other micropython shit
1. mpremote mip install ssd1306