# Formatif F1 — Introduction au Raspberry Pi et capteurs Adafruit

**Cours** : 243-413-SH — Introduction aux objets connectés
**Semaine** : 1
**Type** : Formative (non notée)
**Date limite** : Une semaine après réception du Raspberry Pi

---

## Objectif

Ce formatif vise à vérifier que vous êtes capable de :
1. ✅ Configurer SSH sans mot de passe (depuis Windows)
2. ✅ Installer UV et gérer les dépendances Python
3. ✅ Détecter un capteur I²C avec `i2cdetect`
4. ✅ Lire un capteur BMP280 (température, pression, altitude)
5. ✅ Contrôler un NeoSlider (potentiomètre + LEDs)

---

## Workflow de soumission

⚠️ **IMPORTANT** : Pour que votre travail soit accepté, vous devez **exécuter les tests localement sur le Raspberry Pi AVANT de pousser**.

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKLOAD FORMATIF F1                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Sur votre ordinateur Windows                              │
│     └─ Générer une clé SSH                                    │
│     └─ Copier la clé sur le Pi                                │
│                                                                  │
│  2. Sur le Raspberry Pi (via SSH)                             │
│     └─ Installer UV                                            │
│     └─ Cloner votre dépôt GitHub                             │
│     └─ Créer test_bmp280.py                                   │
│     └─ Exécuter: python3 run_tests.py                         │
│     └─ Corriger les erreurs                                    │
│     └─ Pousser: git add, commit, push                         │
│                                                                  │
│  3. GitHub Actions valide automatiquement                     │
│     └─ Vérifie les marqueurs de tests                         │
│     └─ Confirme que vous avez tout complété                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Instructions détaillées

### Étape 0 : Installation de Raspberry Pi OS

Suivre le guide de Raspberry Pi : https://www.raspberrypi.com/documentation/computers/getting-started.html

### Étape 1 : Connexion SSH sans mot de passe (Windows PowerShell)

#### Générer une clé SSH

```powershell
ssh-keygen -t ed25519 -C "mon-raspberry-pi"
```

- Appuyez **Entrée** pour accepter l'emplacement par défaut
- Appuyez **Entrée** deux fois pour laisser le mot de passe vide

#### Copier la clé sur le Raspberry Pi

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh utilisateur@HOSTNAME.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

> ⚠️ Remplacez `HOSTNAME` par le nom de votre Raspberry Pi et `utilisateur` par votre nom d'utilisateur.

#### Tester la connexion

```powershell
ssh utilisateur@HOSTNAME.local
```

Vous devriez vous connecter **sans entrer de mot de passe**.

---

### Étape 2 : Installer UV et cloner le dépôt

Une fois connecté en SSH sur le Raspberry Pi :

```bash
# Installer UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recharger le shell
source ~/.bashrc

# Configurer Git (IMPORTANT!)
git config --global user.name "Prénom Nom"
git config --global user.email "votre.email@cegepsherbrooke.qc.ca"
git config --global init.defaultbranch main
```

```bash
# Cloner votre dépôt GitHub Classroom
git clone https://github.com/tge-sherbrooke/f1-votre-username.git
cd semaine-1-f1-votre-username
```

---

### Étape 3 : Activer I2C et vérifier les capteurs

```bash
# Activer I2C
sudo raspi-config nonint do_i2c 0

# Installer les outils I2C
sudo apt update && sudo apt install -y i2c-tools

# Scanner le bus I2C
sudo i2cdetect -y 1
```

Vous devriez voir :
- `77` pour le BMP280
- `30` pour le NeoSlider

⚠️ **IMPORTANT** : Les capteurs fonctionnent UNIQUEMENT en 3.3V !

---

### Étape 4 : Créer et tester le BMP280

Créez le fichier `test_bmp280.py` :

```python
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
```

Testez-le :

```bash
uv run test_bmp280.py
```

---

### Étape 5 : Créer et tester le NeoSlider (optionnel)

Créez le fichier `test_neoslider.py` :

```python
# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-seesaw", "adafruit-blinka"]
# ///
"""Test du NeoSlider - Animation arc-en-ciel sur les LEDs."""

import board
import time
from rainbowio import colorwheel
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import neopixel

# Configuration NeoSlider
i2c = board.I2C()
neoslider = Seesaw(i2c, 0x30)
pixels = neopixel.NeoPixel(neoslider, 14, 4, pixel_order=neopixel.GRB)

# Position dans la roue des couleurs
color_pos = 0

while True:
    pixels.fill(colorwheel(color_pos))
    color_pos = (color_pos + 1) % 256
    time.sleep(0.02)
```

Testez-le :

```bash
uv run test_neoslider.py
```

---

### Étape 6 : ⭐ Exécuter les tests locaux

**Ceci est l'étape obligatoire avant de pousser!**

```bash
python3 run_tests.py
```

Le script `run_tests.py` va :
1. ✅ Vérifier que votre clé SSH existe
2. ✅ Vérifier que `test_bmp280.py` est correct
3. ✅ Vérifier que `test_neoslider.py` est correct (optionnel)
4. ✅ Scanner le bus I2C pour détecter les capteurs
5. ✅ Créer des fichiers marqueurs dans `.test_markers/`

Si tous les tests passent, vous verrez :
```
🎉 TOUS LES TESTS SONT PASSÉS!
```

---

### Étape 7 : Pousser votre travail

Une fois les tests passés :

```bash
git add .
git commit -m "feat: tests BMP280 et NeoSlider complétés"
git push
```

GitHub Actions validera automatiquement que vous avez exécuté les tests.

---

## Câblage STEMMA QT

| Fil | Raspberry Pi |
|-----|--------------|
| Rouge (VIN) | 3.3V |
| Noir (GND) | GND |
| Bleu (SDA) | GPIO 2 |
| Jaune (SCL) | GPIO 3 |

⚠️ **VIN doit être connecté à 3.3V, PAS 5V !**

---

## Comprendre la validation

### Pourquoi exécuter `run_tests.py` AVANT de pousser ?

Le formatif F1 utilise une validation en deux temps :

| Étape | Où | Ce qui est validé |
|-------|----|-------------------|
| **run_tests.py** | Sur Raspberry Pi | - Clé SSH installée<br>- Scripts créés<br>- Capteurs détectés |
| **GitHub Actions** | Automatique après push | - Les marqueurs existent<br>- Syntaxe Python valide |

Cette approche garantit que vous avez **réellement** travaillé sur le matériel tout en bénéficiant de l'automatisation GitHub.

### Que se passe-t-il si je pousse sans exécuter les tests ?

GitHub Actions affichera une erreur :
```
❌ ERREUR: Les tests locaux n'ont pas été exécutés!
```

Vous devrez alors exécuter `python3 run_tests.py` sur le Raspberry Pi et repousser.

---

## Livrables

Dans ce dépôt, vous devez avoir :

- [ ] `test_bmp280.py` — Script de lecture du capteur BMP280
- [ ] `test_neoslider.py` — Script de test du NeoSlider (optionnel)
- [ ] `.test_markers/` — Dossier créé par `run_tests.py` (ne pas éditer manuellement!)

---

## Résumé des commandes

```bash
# ===== SUR WINDOWS POWERSHELL =====
ssh-keygen -t ed25519 -C "mon-raspberry-pi"
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh utilisateur@HOSTNAME.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
ssh utilisateur@HOSTNAME.local

# ===== SUR RASPBERRY PI =====
# Installer UV
curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc

# Configurer Git
git config --global user.name "Prénom Nom"
git config --global user.email "votre.email@etu.cegep.qc.ca"

# Cloner le dépôt
git clone https://github.com/organisation/semaine-1-f1-votre-username.git
cd semaine-1-f1-votre-username

# Activer I2C
sudo raspi-config nonint do_i2c 0
sudo apt install -y i2c-tools

# Scanner I2C
sudo i2cdetect -y 1

# ===== TESTER LES CAPTEURS =====
uv run test_bmp280.py
uv run test_neoslider.py

# ===== EXÉCUTER LES TESTS =====
python3 run_tests.py

# ===== POUSSER =====
git add .
git commit -m "feat: tests complétés"
git push
```

---

## Ressources

- [Guide de l'étudiant](../deliverables/activites/semaine-1/labo/guide-étudiant.md)
- [Guide de dépannage](../deliverables/activites/semaine-1/labo/guide-depannage.md)

---

Bonne chance ! 🚀
