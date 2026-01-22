#!/usr/bin/env python3
"""
Test runner local pour le Formatif F1 - Semaine 1

Ce script exécute les tests localement sur le Raspberry Pi et crée
des fichiers marqueurs qui seront vérifiés par GitHub Actions.

Usage: python3 run_tests.py
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Couleurs ANSI pour le terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def check_ssh_key():
    """
    Vérifie qu'une clé SSH publique existe et crée le marqueur.
    """
    print_header("VÉRIFICATION SSH")

    ssh_dir = Path.home() / ".ssh"
    pub_keys = [
        ssh_dir / "id_ed25519.pub",
        ssh_dir / "id_rsa.pub",
    ]

    key_found = False
    for key_path in pub_keys:
        if key_path.exists():
            key_found = True
            print_success(f"Clé SSH publique trouvée: {key_path.name}")

            # Lire le contenu de la clé publique
            key_content = key_path.read_text().strip()
            print(f"   {key_content[:40]}...")

            # Vérifier que authorized_keys existe sur le Pi (local check)
            authorized_keys = Path.home() / ".ssh" / "authorized_keys"
            if authorized_keys.exists():
                auth_content = authorized_keys.read_text()
                if key_content.split()[1] in auth_content:  # Comparer la partie clé
                    print_success("La clé est dans authorized_keys (connexion sans mot de passe)")
                else:
                    print_warning("authorized_keys existe mais ne contient pas cette clé")
            else:
                print_warning("authorized_keys n'existe pas encore")
                print("   Sur Windows PowerShell:")
                print('   type $env:USERPROFILE\\.ssh\\id_ed25519.pub | ssh user@HOSTNAME.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"')

            break

    if not key_found:
        print_error("Aucune clé SSH publique trouvée")
        print("\n📚 Pour générer une clé SSH:")
        print("   ssh-keygen -t ed25519 -C \"mon-raspberry-pi\"")
        print("   (Appuyez 3x sur Entrée pour les valeurs par défaut)")
        return False

    # Créer le marqueur SSH
    marker = Path(__file__).parent / ".test_markers" / "ssh_key_verified.txt"
    marker.parent.mkdir(exist_ok=True)
    marker.write_text(f"SSH key verified: {datetime.now().isoformat()}\n")
    print_success(f"Marqueur SSH créé: {marker}")

    return True


def check_bmp280_script():
    """
    Vérifie le script test_bmp280.py.
    """
    print_header("VÉRIFICATION TEST_BMP280.PY")

    script_path = Path(__file__).parent / "test_bmp280.py"

    if not script_path.exists():
        print_error("Fichier test_bmp280.py introuvable")
        return False

    print_success("Fichier test_bmp280.py trouvé")

    # Vérifier la syntaxe
    try:
        with open(script_path) as f:
            compile(f.read(), script_path, 'exec')
        print_success("Syntaxe Python valide")
    except SyntaxError as e:
        print_error(f"Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        return False

    # Vérifier les imports
    content = script_path.read_text()
    required = ['board', 'adafruit_bmp280']

    for imp in required:
        if imp in content:
            print_success(f"Import trouvé: {imp}")
        else:
            print_error(f"Import manquant: {imp}")
            return False

    # Vérifier les dépendances UV
    if 'dependencies' in content and 'adafruit-circuitpython-bmp280' in content:
        print_success("Dépendances UV configurées")
    else:
        print_warning("Dépendances UV non trouvées (décommentées dans le script?)")

    # Créer le marqueur
    marker = Path(__file__).parent / ".test_markers" / "bmp280_script_verified.txt"
    marker.write_text(f"BMP280 script verified: {datetime.now().isoformat()}\n")
    print_success(f"Marqueur BMP280 créé: {marker}")

    return True


def check_neoslider_script():
    """
    Vérifie le script test_neoslider.py.
    """
    print_header("VÉRIFICATION TEST_NEOSLIDER.PY")

    script_path = Path(__file__).parent / "test_neoslider.py"

    if not script_path.exists():
        print_warning("test_neoslider.py introuvable (optionnel)")
        return True  # Non obligatoire

    print_success("Fichier test_neoslider.py trouvé")

    # Vérifier la syntaxe
    try:
        with open(script_path) as f:
            compile(f.read(), script_path, 'exec')
        print_success("Syntaxe Python valide")
    except SyntaxError as e:
        print_error(f"Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        return False

    # Vérifier les imports
    content = script_path.read_text()
    required = ['board', 'adafruit_seesaw']

    for imp in required:
        if imp in content:
            print_success(f"Import trouvé: {imp}")
        else:
            print_error(f"Import manquant: {imp}")
            return False

    # Créer le marqueur
    marker = Path(__file__).parent / ".test_markers" / "neoslider_script_verified.txt"
    marker.write_text(f"NeoSlider script verified: {datetime.now().isoformat()}\n")
    print_success(f"Marqueur NeoSlider créé: {marker}")

    return True


def run_hardware_tests():
    """
    Tente d'exécuter les tests matériels (si sur Raspberry Pi).
    """
    print_header("TESTS MATÉRIEL (Raspberry Pi)")

    # Vérifier si on est sur un Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            is_rpi = 'Raspberry Pi' in cpuinfo or 'Broadcom' in cpuinfo
    except:
        is_rpi = False

    if not is_rpi:
        print_warning("Pas sur Raspberry Pi - tests matériels skipés")
        print("   Exécutez ce script sur le Raspberry Pi pour les tests matériels")
        return True

    print_success("Raspberry Pi détecté")

    # Vérifier i2cdetect
    try:
        result = subprocess.run(
            ['sudo', 'i2cdetect', '-y', '1'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            output = result.stdout
            if '77' in output:
                print_success("BMP280 détecté à l'adresse 0x77")
            else:
                print_warning("BMP280 non détecté à 0x77 - vérifiez le câblage")

            if '30' in output:
                print_success("NeoSlider détecté à l'adresse 0x30")
            else:
                print_warning("NeoSlider non détecté à 0x30 (optionnel)")

            # Créer le marqueur matériel
            marker = Path(__file__).parent / ".test_markers" / "hardware_detected.txt"
            marker.write_text(f"Hardware scan: {datetime.now().isoformat()}\n{output}\n")
            print_success(f"Marqueur matériel créé: {marker}")
        else:
            print_error("i2cdetect a échoué")
            return False
    except FileNotFoundError:
        print_warning("i2cdetect non trouvé - installez: sudo apt install i2c-tools")
    except subprocess.TimeoutExpired:
        print_warning("i2cdetect timeout - vérifiez I2C")
    except Exception as e:
        print_warning(f"Erreur i2cdetect: {e}")

    return True


def update_gitignore():
    """
    Met à jour .gitignore pour permettre de commettre les marqueurs de tests.
    Supprime la ligne '.test_markers/' du .gitignore pour permettre aux étudiants
    de pousser les marqueurs créés par run_tests.py.
    """
    gitignore_path = Path(__file__).parent / ".gitignore"
    marker_dir = Path(__file__).parent / ".test_markers"

    # Si les marqueurs existent, on permet de les commettre
    if not marker_dir.exists():
        return

    if not gitignore_path.exists():
        return

    # Lire le .gitignore actuel
    lines = gitignore_path.read_text().splitlines()

    # Filtrer les lignes qui excluent .test_markers
    new_lines = []
    modified = False
    for line in lines:
        # Ignorer les patterns qui excluent .test_markers ou son contenu
        if '.test_markers' in line and not line.strip().startswith('#'):
            # Remplacer par un commentaire explicatif
            if not modified:
                new_lines.append('# .test_markers/ is now allowed (created by run_tests.py)')
                modified = True
        else:
            new_lines.append(line)

    if modified:
        gitignore_path.write_text('\n'.join(new_lines) + '\n')
        print_success(".gitignore mis à jour - les marqueurs peuvent être commités")


def create_test_summary():
    """
    Crée un résumé des tests pour GitHub Actions.
    """
    marker_dir = Path(__file__).parent / ".test_markers"
    summary_file = marker_dir / "test_summary.txt"

    markers = list(marker_dir.glob("*_verified.txt")) + list(marker_dir.glob("*_detected.txt"))

    summary = f"""Test Summary for Formatif F1
Generated: {datetime.now().isoformat()}
Tests Run: {len(markers)}

Markers:
"""
    for marker in sorted(markers):
        summary += f"  - {marker.stem}: {marker.read_text().strip()}\n"

    summary_file.write_text(summary)
    print_success(f"Résumé des tests créé: {summary_file}")


def main():
    """
    Fonction principale.
    """
    print(f"\n{Colors.BOLD}Formatif F1 - Test Runner Local{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    results = {
        "SSH": check_ssh_key(),
        "BMP280": check_bmp280_script(),
        "NeoSlider": check_neoslider_script(),
        "Hardware": run_hardware_tests(),
    }

    # Créer le résumé
    create_test_summary()

    # Afficher le résultat final
    print_header("RÉSULTAT FINAL")

    all_passed = all(results.values())

    for test, passed in results.items():
        if passed:
            print_success(f"{test}: OK")
        else:
            print_error(f"{test}: ÉCHEC")

    print()

    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES TESTS SONT PASSÉS!{Colors.END}")

        # Met à jour .gitignore pour permettre de commettre les marqueurs
        update_gitignore()

        print("\n📤 Vous pouvez maintenant pousser vos modifications:")
        print("   git add .")
        print("   git commit -m \"feat: tests locaux passés\"")
        print("   git push")

        # Créer le marqueur final de succès
        marker = Path(__file__).parent / ".test_markers" / "all_tests_passed.txt"
        marker.write_text(f"All tests passed: {datetime.now().isoformat()}\n")

        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  CERTAINS TESTS ONT ÉCHOUÉ{Colors.END}")
        print("\nCorrigez les erreurs ci-dessus et relancez:")
        print("   python3 run_tests.py")

        return 1


if __name__ == "__main__":
    sys.exit(main())
