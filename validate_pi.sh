#!/bin/bash
# Script de validation pour le Formatif F1 sur Raspberry Pi
# Exécutez: bash validate_pi.sh

echo "========================================"
echo "VALIDATION FORMATIF F1 - Raspberry Pi"
echo "========================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteur
passed=0
failed=0

# Fonction pour vérifier une commande
check() {
    local name="$1"
    local command="$2"

    echo -n "Checking $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((passed++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((failed++))
        return 1
    fi
}

# 1. Vérifier Python 3
check "Python 3 installed" "which python3"

# 2. Vérifier pip
check "pip3 installed" "which pip3"

# 3. Vérifier I2C tools
check "i2c-tools installed" "which i2cdetect"

# 4. Vérifier que I2C est activé
echo -n "Checking I2C enabled... "
if i2cdetect -y 1 > /dev/null 2>&1 || [ -e /dev/i2c-1 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((passed++))
else
    echo -e "${RED}✗ FAIL${NC} (Run: sudo raspi-config → Interface → I2C)"
    ((failed++))
fi

# 5. Vérifier les bibliothèques Python
echo ""
echo "Checking Python libraries..."
check "adafruit_bmp installed" "python3 -c 'import adafruit_bmp'"
check "board module installed" "python3 -c 'import board'"

# 6. Scanner le bus I2C
echo ""
echo "Scanning I2C bus for BMP280..."
if i2cdetect -y 1 2>/dev/null | grep -q "77"; then
    echo -e "${GREEN}✓ BMP280 detected at 0x77${NC}"
    ((passed++))
else
    echo -e "${RED}✗ No BMP280 found at 0x77${NC}"
    echo "  Check wiring:"
    echo "  - VIN → 3.3V (NOT 5V!)"
    echo "  - GND → GND"
    echo "  - SDA → GPIO 2 (SDA)"
    echo "  - SCL → GPIO 3 (SCL)"
    ((failed++))
fi

# 7. Vérifier le script capteur.py
echo ""
if [ -f "capteur.py" ]; then
    echo -e "${GREEN}✓ capteur.py exists${NC}"
    ((passed++))

    echo -n "Testing capteur.py execution... "
    if timeout 10 python3 capteur.py > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((passed++))

        echo ""
        echo "Sample output:"
        echo "----------------------------------------"
        python3 capteur.py
        echo "----------------------------------------"
    else
        echo -e "${RED}✗ FAIL${NC} (Script has errors)"
        ((failed++))
    fi
else
    echo -e "${YELLOW}⚠ capteur.py not found${NC}"
    echo "  Create it with the code from README.md"
    ((failed++))
fi

# Résumé
echo ""
echo "========================================"
echo "RÉSUMÉ DE LA VALIDATION"
echo "========================================"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 Tout fonctionne! Vous pouvez pousser votre code.${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Corrigez les erreurs avant de continuer.${NC}"
    exit 1
fi
