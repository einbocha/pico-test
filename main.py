from machine import Pin, I2C
import ssd1306

# I2C1 on GP21 (SDA) and GP22 (SCL)
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)

# Adjust to your display resolution
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

oled.fill(0)
oled.text("Hello, Pico!", 0, 0)
oled.show()