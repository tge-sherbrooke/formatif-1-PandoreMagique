# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-bmp280", "adafruit-circuitpython-seesaw", "adafruit-blinka"]
# ///
"""Validation complète de la configuration Raspberry Pi."""

import sys

def test_i2c():
    """Test de la communication I2C."""
    try:
        import board
        i2c = board.I2C()
        print("✓ I2C OK")
        return i2c
    except Exception as e:
        print(f"✗ I2C ERREUR: {e}")
        return None

def test_bmp280(i2c):
    """Test du capteur BMP280."""
    try:
        import adafruit_bmp280
        sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
        temp = sensor.temperature
        print(f"✓ BMP280 OK - Température: {temp:.1f}°C")
        return True
    except Exception as e:
        print(f"✗ BMP280 ERREUR: {e}")
        return False

def test_neoslider(i2c):
    """Test du NeoSlider - LEDs."""
    try:
        from adafruit_seesaw.seesaw import Seesaw
        from adafruit_seesaw import neopixel

        neoslider = Seesaw(i2c, addr=0x30)
        pixels = neopixel.NeoPixel(neoslider, 14, 4, pixel_order=neopixel.GRB)

        # Test: allumer en vert
        pixels.fill((0, 255, 0))
        print("✓ NeoSlider LEDs OK - LEDs allumées en vert")
        return True, pixels
    except Exception as e:
        print(f"✗ NeoSlider ERREUR: {e}")
        return False, None

if __name__ == "__main__":
    print("=" * 50)
    print("VALIDATION RASPBERRY PI")
    print("=" * 50)

    i2c = test_i2c()
    if not i2c:
        sys.exit(1)

    bmp_ok = test_bmp280(i2c)
    neo_ok, pixels = test_neoslider(i2c)

    # Éteindre les LEDs avant de terminer
    if pixels:
        try:
            pixels.fill((0, 0, 0))
        except:
            pass

    print("=" * 50)
    if bmp_ok and neo_ok:
        print("✓ TOUS LES TESTS RÉUSSIS")
    else:
        print("✗ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)
