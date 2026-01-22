#!/usr/bin/env python3
"""
Script de correction pour le Formatif F1 — Semaine 1
Cours 243-413-SH — Introduction aux objets connectés

Ce script:
1. Exécute les tests pytest sur le dépôt de l'étudiant
2. Calcule la note selon les grilles permanentes
3. Génère une rétroaction détaillée
4. Produit un rapport exportable

Usage:
    python3 correction.py <chemin_dépôt_étudiant>

Exemple:
    python3 correction.py ../etudiants/du-pierre-julien-f1
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import argparse


# Configuration de l'évaluation
CONFIG = {
    "cours": "243-413-SH",
    "titre": "Formatif F1 — Introduction au Raspberry Pi et STEMMA QT",
    "semaine": 1,
    "type": "Formative (non notée)",
    "indicateurs": {
        "IND-00SX-E": {
            "ponderation": 50,
            "critere": "Exécution — Environnement & Déploiement",
            "description": "Préparer l'environnement de développement et déployer l'application",
            "critères_performance": ["2.1", "2.2", "2.3", "2.4", "2.6"]
        },
        "IND-00SX-D": {
            "ponderation": 50,
            "critere": "Conception — Programmation",
            "description": "Programmer la logique applicative pour l'acquisition de données",
            "critères_performance": ["4.1", "4.3"]
        }
    }
}


def executer_tests(repo_path):
    """
    Exécute les tests pytest sur le dépôt de l'étudiant.

    Args:
        repo_path: Chemin vers le dépôt de l'étudiant

    Returns:
        dict: Résultats des tests avec détails
    """
    print(f"🔍 Exécution des tests sur: {repo_path}")

    # Construire la commande pytest
    cmd = [
        sys.executable, "-m", "pytest",
        str(repo_path / "tests"),
        "-v",
        "--tb=short",
        "--json-report",
        f"--json-report-file={repo_path}/test_results.json"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(repo_path)
        )

        # Lire les résultats JSON si disponibles
        test_results_path = repo_path / "test_results.json"
        if test_results_path.exists():
            with open(test_results_path) as f:
                return json.load(f)

        # Sinon, parser depuis stdout
        return parser_sortie_pytest(result.stdout, result.returncode)

    except subprocess.TimeoutExpired:
        return {"erreur": "Timeout - Les tests prennent trop de temps"}
    except FileNotFoundError:
        return {"erreur": "pytest non installé ou tests introuvables"}
    except Exception as e:
        return {"erreur": f"Erreur lors des tests: {str(e)}"}


def parser_sortie_pytest(stdout, returncode):
    """
    Parse la sortie texte de pytest si le rapport JSON n'est pas disponible.

    Args:
        stdout: Sortie standard de pytest
        returncode: Code de retour de pytest

    Returns:
        dict: Résultats parsés
    """
    result = {
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        },
        "tests": []
    }

    # Parsing simple de la sortie
    for line in stdout.split('\n'):
        line = line.strip()
        if '::' in line and ('PASSED' in line or 'FAILED' in line):
            parts = line.split()
            test_name = parts[0].split('::')[-1]
            status = parts[1] if len(parts) > 1 else "UNKNOWN"

            result["summary"]["total"] += 1
            if status == "PASSED":
                result["summary"]["passed"] += 1
            elif status == "FAILED":
                result["summary"]["failed"] += 1
            else:
                result["summary"]["skipped"] += 1

            result["tests"].append({
                "name": test_name,
                "outcome": status.lower()
            })

    result["summary"]["duration"] = 0
    return result


def calculer_notes(resultats_tests):
    """
    Calcule les notes selon les grilles permanentes.

    Args:
        resultats_tests: Résultats des tests pytest

    Returns:
        dict: Notes par indicateur et note finale
    """
    notes = {
        "IND-00SX-E": {"score": 0, "niveau": 0, "retroaction": ""},
        "IND-00SX-D": {"score": 0, "niveau": 0, "retroaction": ""},
        "finale": 0
    }

    # Extraire les résultats des tests
    tests = resultats_tests.get("tests", [])
    test_status = {t["name"]: t["outcome"] for t in tests}

    # Évaluer IND-00SX-E (Environnement)
    score_e = 0
    if test_status.get("test_requirements_present") == "passed":
        score_e += 50
    if test_status.get("test_import_board") == "passed" or test_status.get("test_import_si7021") == "passed":
        score_e += 50

    notes["IND-00SX-E"]["score"] = score_e
    notes["IND-00SX-E"]["niveau"] = determiner_niveau(score_e)
    notes["IND-00SX-E"]["retroaction"] = generer_retroaction("IND-00SX-E", score_e)

    # Évaluer IND-00SX-D (Programmation)
    score_d = 0
    if test_status.get("test_script_exists") == "passed":
        score_d += 20
    if test_status.get("test_script_has_required_imports") == "passed":
        score_d += 20
    if test_status.get("test_script_creates_sensor") == "passed":
        score_d += 20
    if test_status.get("test_script_executes") == "passed":
        score_d += 20
    if test_status.get("test_script_output_format") == "passed":
        score_d += 20

    notes["IND-00SX-D"]["score"] = score_d
    notes["IND-00SX-D"]["niveau"] = determiner_niveau(score_d)
    notes["IND-00SX-D"]["retroaction"] = generer_retroaction("IND-00SX-D", score_d)

    # Note finale (pondérée)
    notes["finale"] = (score_e * 0.5) + (score_d * 0.5)

    return notes


def determiner_niveau(score):
    """
    Détermine le niveau selon les grilles permanentes (0%, 35%, 60%, 85%, 100%).

    Args:
        score: Score brut (0-100)

    Returns:
        int: Niveau (0, 35, 60, 85, ou 100)
    """
    if score >= 100:
        return 100
    elif score >= 85:
        return 85
    elif score >= 60:
        return 60
    elif score >= 35:
        return 35
    else:
        return 0


def generer_retroaction(indicateur, score):
    """
    Génère un message de rétroaction personnalisé.

    Args:
        indicateur: Code de l'indicateur (IND-00SX-E ou IND-00SX-D)
        score: Score obtenu

    Returns:
        str: Message de rétroaction
    """
    messages = {
        "IND-00SX-E": {
            100: "🎉 Excellent ! L'environnement est parfaitement configuré. Les dépendances sont correctement installées.",
            85: "✅ Très bon ! L'environnement est bien configuré. Tout fonctionne correctement.",
            60: "👍 L'environnement de base est en place. Quelques améliorations mineures possibles.",
            35: "⚠️ L'environnement est partiellement configuré. Vérifiez requirements.txt.",
            0: "❌ L'environnement n'est pas configuré. Ajoutez les dépendances dans requirements.txt."
        },
        "IND-00SX-D": {
            100: "🎉 Parfait ! Le script est fonctionnel, bien structuré et produit le résultat attendu.",
            85: "✅ Très bon travail ! Le script fonctionne correctement et affiche les données.",
            60: "👍 Le script fonctionne et affiche les données essentielles.",
            35: "⚠️ Le script existe mais a des problèmes. Vérifiez la structure et le format.",
            0: "❌ Le script n'est pas fonctionnel. Créez capteur.py avec la structure requise."
        }
    }

    niveau = determiner_niveau(score)
    return messages.get(indicateur, {}).get(niveau, "Rétroaction non disponible")


def afficher_rapport(etudiant, resultats_tests, notes):
    """
    Affiche un rapport détaillé de la correction.

    Args:
        etudiant: Nom de l'étudiant (ou ID)
        resultats_tests: Résultats bruts des tests
        notes: Notes calculées
    """
    print("\n" + "="*70)
    print(f"📊 RAPPORT DE CORRECTION — {CONFIG['titre']}")
    print("="*70)
    print(f"Étudiant: {etudiant}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Cours: {CONFIG['cours']}")
    print(f"Type: {CONFIG['type']}")

    # Résumé des tests
    print("\n" + "-"*70)
    print("RÉSUMÉ DES TESTS")
    print("-"*70)

    summary = resultats_tests.get("summary", {})
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)

    print(f"Tests exécutés: {total}")
    print(f"✅ Réussis: {passed}")
    print(f"❌ Échoués: {failed}")

    # Détail par indicateur
    print("\n" + "-"*70)
    print("ÉVALUATION PAR INDICATEUR")
    print("-"*70)

    for indicateur, config in CONFIG["indicateurs"].items():
        note = notes[indicateur]
        print(f"\n{indicateur} — {config['critere']}")
        print(f"  Critères de performance: {', '.join(config['critères_performance'])}")
        print(f"  Score: {note['score']:.0f}%")
        print(f"  Niveau: {note['niveau']}%")
        print(f"  Rétroaction: {note['retroaction']}")

    # Note finale
    print("\n" + "-"*70)
    print("NOTE FINALE")
    print("-"*70)
    print(f"📈 Score global: {notes['finale']:.1f}%")

    # Message formatif
    print("\n" + "="*70)
    print("💡 RAPPEL IMPORTANT")
    print("="*70)
    print("Cette évaluation est FORMATIVE et NON NOTÉE.")
    print("Son but est de vous donner une rétroaction pour vous améliorer.")
    print("\nSi vous avez des échecs:")
    print("1. Lisez attentivement la rétroaction ci-dessus")
    print("2. Consultez le guide de dépannage")
    print("3. Corrigez votre code")
    print("4. Pussez et relancez les tests")
    print("\nN'hésitez pas à demander de l'aide à l'enseignant!")
    print("="*70 + "\n")


def exporter_excel(etudiants_resultats, chemin_sortie):
    """
    Exporte les résultats vers un fichier Excel.

    Args:
        etudiants_resultats: Liste des résultats par étudiant
        chemin_sortie: Chemin du fichier de sortie

    Returns:
        bool: True si succès, False sinon
    """
    try:
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Résultats F1"

        # En-têtes
        headers = ["Étudiant", "IND-00SX-E (%)", "IND-00SX-D (%)", "Note finale (%)", "Rétroaction"]
        ws.append(headers)

        # Données
        for result in etudiants_resultats:
            ws.append([
                result["etudiant"],
                result["notes"]["IND-00SX-E"]["score"],
                result["notes"]["IND-00SX-D"]["score"],
                result["notes"]["finale"],
                result["notes"]["IND-00SX-E"]["retroaction"][:50] + "..."
            ])

        wb.save(chemin_sortie)
        print(f"✅ Résultats exportés vers: {chemin_sortie}")
        return True

    except ImportError:
        print("⚠️ openpyxl non installé. Installation: pip install openpyxl")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'export Excel: {e}")
        return False


def main():
    """
    Fonction principale du script de correction.
    """
    parser = argparse.ArgumentParser(description="Script de correction pour F1")
    parser.add_argument("repo", help="Chemin vers le dépôt de l'étudiant")
    parser.add_argument("--export", help="Chemin pour exporter les résultats en Excel")
    parser.add_argument("--batch", help="Traiter tous les dépôts dans le dossier spécifié")

    args = parser.parse_args()

    # Mode batch: traiter plusieurs dépôts
    if args.batch:
        tous_resultats = []
        batch_path = Path(args.batch)

        for repo_dir in batch_path.iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith('.'):
                print(f"\n{'='*70}")
                print(f"Traitement de: {repo_dir.name}")
                print('='*70)

                resultats_tests = executer_tests(repo_dir)
                notes = calculer_notes(resultats_tests)

                tous_resultats.append({
                    "etudiant": repo_dir.name,
                    "resultats": resultats_tests,
                    "notes": notes
                })

                afficher_rapport(repo_dir.name, resultats_tests, notes)

        # Exporter si demandé
        if args.export:
            exporter_excel(tous_resultats, args.export)

    # Mode single: un seul dépôt
    else:
        repo_path = Path(args.repo)

        if not repo_path.exists():
            print(f"❌ Erreur: Le dépôt n'existe pas: {repo_path}")
            sys.exit(1)

        etudiant = repo_path.name
        resultats_tests = executer_tests(repo_path)
        notes = calculer_notes(resultats_tests)

        afficher_rapport(etudiant, resultats_tests, notes)


if __name__ == "__main__":
    main()
