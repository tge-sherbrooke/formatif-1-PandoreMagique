# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-bmp280", "adafruit-blinka"]
# ///
"""Test du capteur BMP280 via STEMMA QT/I2C."""

import board
import adafruit_bmp280

i2c = board.I2C()
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)

print(f"Température: {sensor.temperature:.1f} °C")
print(f"Pression: {sensor.pressure:.1f} hPa")
print(f"Altitude: {sensor.altitude:.1f} m")
