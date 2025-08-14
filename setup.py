# ==========================================
# ÉTAPE 1 : SETUP DU PROJET SCR PROMPT GENERATOR
# ==========================================

# 1. Structure des répertoires à créer
"""
scr_prompt_generator/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py
│   │   ├── pdf_parser.py
│   │   └── html_parser.py
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── templates.py
│   │   └── generator.py
│   └── main.py
├── data/
│   └── documents/
├── tests/
│   ├── __init__.py
│   └── test_basic.py
├── requirements.txt
├── setup.py
└── README.md
"""

# 2. Contenu du fichier requirements.txt
requirements_content = """
# Base dependencies
pandas>=1.5.0
numpy>=1.21.0
sqlite3  # Built-in with Python
pathlib  # Built-in with Python
logging  # Built-in with Python

# Document processing
PyPDF2>=3.0.0
pdfplumber>=0.7.0
beautifulsoup4>=4.11.0
requests>=2.28.0

# Configuration and CLI
pyyaml>=6.0
argparse  # Built-in with Python

# Optional but recommended
python-magic>=0.4.27  # For file type detection
"""

# 3. Script de setup automatique
import os
import subprocess
import sys


def create_project_structure():
    """Création automatique de la structure du projet"""

    # Répertoires à créer
    directories = [
        "scr_prompt_generator",
        "scr_prompt_generator/src",
        "scr_prompt_generator/src/config",
        "scr_prompt_generator/src/parsers",
        "scr_prompt_generator/src/knowledge",
        "scr_prompt_generator/src/prompts",
        "scr_prompt_generator/data",
        "scr_prompt_generator/data/documents",
        "scr_prompt_generator/tests"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Créé: {directory}/")

    # Fichiers __init__.py
    init_files = [
        "scr_prompt_generator/src/__init__.py",
        "scr_prompt_generator/src/config/__init__.py",
        "scr_prompt_generator/src/parsers/__init__.py",
        "scr_prompt_generator/src/knowledge/__init__.py",
        "scr_prompt_generator/src/prompts/__init__.py",
        "scr_prompt_generator/tests/__init__.py"
    ]

    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('"""Package initialization"""')
        print(f"✅ Créé: {init_file}")

    # requirements.txt
    with open("requirements.txt", "w") as f:
        f.write(requirements_content.strip())
    print("✅ Créé: requirements.txt")

    print("\n🎉 Structure du projet créée avec succès!")
    print("📁 Naviguez vers: cd scr_prompt_generator")
    print("📦 Installez les dépendances: pip install -r requirements.txt")


if __name__ == "__main__":
    print("🚀 CRÉATION DE LA STRUCTURE DU PROJET SCR PROMPT GENERATOR")
    print("=" * 60)

    # Vérification de Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        sys.exit(1)

    create_project_structure()

    # Instructions pour la suite
    print("\n📋 PROCHAINES ÉTAPES:")
    print("1. cd scr_prompt_generator")
    print("2. pip install -r requirements.txt")
    print("3. Prêt pour l'étape 2 !")