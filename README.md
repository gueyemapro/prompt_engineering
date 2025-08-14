# 🚀 SCR Prompt Generator - Solvabilité 2

> **Générateur de prompts optimisés pour l'IA dans le domaine de Solvabilité 2**

Un système intelligent qui transforme vos documents réglementaires en prompts ultra-précis pour Claude, GPT-4, Gemini et autres IA, spécialement conçu pour les actuaires et experts en Solvabilité 2.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 📋 Table des Matières

- [🎯 Vue d'ensemble](#-vue-densemble)
- [✨ Fonctionnalités principales](#-fonctionnalités-principales)
- [🏗️ Architecture](#️-architecture)
- [⚙️ Installation](#️-installation)
- [🚀 Démarrage rapide](#-démarrage-rapide)
- [📖 Guide d'utilisation](#-guide-dutilisation)
- [📚 Gestion des documents](#-gestion-des-documents)
- [🤖 IA supportées](#-ia-supportées)
- [🎯 Modules SCR](#-modules-scr)
- [📊 Exemples concrets](#-exemples-concrets)
- [🔧 Configuration avancée](#-configuration-avancée)
- [🧪 Tests](#-tests)
- [📈 Performance](#-performance)
- [🤝 Contribution](#-contribution)
- [📄 License](#-license)

## 🎯 Vue d'ensemble

### Problème résolu

Les actuaires passent des heures à rédiger des prompts techniques pour obtenir des réponses précises sur Solvabilité 2. Ce système automatise cette tâche en :

- **Analysant** vos documents réglementaires (PDF, HTML)
- **Extrayant** automatiquement les concepts et articles SCR
- **Générant** des prompts optimisés par IA et niveau d'expertise
- **Personnalisant** selon vos besoins spécifiques

### Résultat

Des prompts **10x plus efficaces** qui donnent des réponses techniques précises avec références réglementaires exactes.

## ✨ Fonctionnalités principales

### 🧠 Intelligence Documentaire
- **Parsing automatique** PDF/HTML avec extraction de concepts SCR
- **Base de connaissances** SQLite avec indexation intelligente
- **Détection automatique** d'articles réglementaires (180, 181, etc.)
- **Scoring de fiabilité** des sources (règlements UE = 1.0, papers = 0.8)

### 🎯 Génération de Prompts Optimisés
- **Templates spécialisés** par IA (Claude, GPT-4, Gemini)
- **Adaptation au niveau** (junior → expert réglementaire)
- **Enrichissement contextuel** avec vos documents
- **Recommandations d'utilisation** personnalisées

### 🔄 Workflow Intégré
- **CLI complet** pour usage quotidien
- **API programmatique** pour intégration
- **Traitement en lot** de documents
- **Export/import** de la base de connaissances

### 📊 Analytics et Monitoring
- **Statistiques détaillées** par module SCR
- **Diagnostic de santé** du système
- **Métriques de qualité** des prompts générés
- **Traçabilité complète** des sources

## 🏗️ Architecture

```
scr_prompt_generator/
├── 📁 src/                          # Code source principal
│   ├── 📁 config/                   # Configuration et enums
│   │   ├── settings.py              # Paramètres globaux
│   │   └── __init__.py
│   ├── 📁 knowledge/                # Gestion de la base de connaissances
│   │   ├── database.py              # Interface SQLite
│   │   ├── models.py                # Modèles de données
│   │   └── __init__.py
│   ├── 📁 parsers/                  # Parsers de documents
│   │   ├── base_parser.py           # Interface abstraite
│   │   ├── pdf_parser.py            # Parser PDF (PyPDF2 + pdfplumber)
│   │   ├── html_parser.py           # Parser HTML/Web (BeautifulSoup)
│   │   └── __init__.py
│   ├── 📁 prompts/                  # Génération de prompts
│   │   ├── templates.py             # Templates par IA
│   │   ├── generator.py             # Moteur de génération
│   │   └── __init__.py
│   └── main.py                      # Orchestrateur principal
├── 📁 data/                         # Données et documents
│   ├── 📁 documents/                # Documents sources
│   │   ├── 📁 regulations/          # Règlements UE
│   │   ├── 📁 eiopa/               # Guidelines EIOPA
│   │   ├── 📁 expert_papers/       # Documents d'experts
│   │   └── 📁 internal/            # Documents internes
│   └── scr_knowledge.db            # Base de données SQLite
├── 📁 tests/                        # Tests automatisés
├── 📁 logs/                         # Fichiers de log
├── cli.py                          # Interface ligne de commande
├── requirements.txt                # Dépendances Python
└── README.md                       # Cette documentation
```

### Composants Clés

1. **SCRPromptGenerator** : Orchestrateur principal
2. **SCRKnowledgeBase** : Gestion de la base de données
3. **PromptEngineer** : Moteur de génération optimisée
4. **DocumentParsers** : Extraction intelligente de contenu

## ⚙️ Installation

### Prérequis

- **Python 3.8+** (testé jusqu'à 3.12)
- **pip** pour la gestion des dépendances
- **Espace disque** : 100MB minimum

### Installation Standard

```bash
# 1. Cloner ou télécharger le projet
git clone <repository-url>
cd scr_prompt_generator

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser le projet
python cli.py init --create-sample-config

# 5. Vérifier l'installation
python cli.py health
```

### Installation Développeur

```bash
# Installation avec dépendances de développement
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Lancer les tests
python -m pytest tests/

# Vérification du code
black src/
flake8 src/
```

### Dépendances Principales

```
pandas>=1.5.0          # Manipulation de données
numpy>=1.21.0          # Calculs numériques
PyPDF2>=3.0.0          # Parsing PDF
pdfplumber>=0.7.0      # Extraction avancée PDF
beautifulsoup4>=4.11.0 # Parsing HTML
requests>=2.28.0       # Requêtes HTTP
pyyaml>=6.0            # Configuration YAML
```

## 🚀 Démarrage rapide

### 1. Test de base (30 secondes)

```bash
# Vérification que tout fonctionne
python cli.py stats

# Génération d'un premier prompt
python cli.py generate \
  --ai claude-sonnet-4 \
  --level expert \
  --module spread \
  --output premier_prompt.txt

# Vérifier le résultat
cat premier_prompt.txt
```

### 2. Ajout d'un document test (1 minute)

```bash
# Utiliser le script de test intégré
python add_documents_test.py

# Vérifier l'ajout
python cli.py stats --detailed

# Générer un prompt enrichi
python cli.py generate \
  --ai claude-sonnet-4 \
  --level expert \
  --module spread \
  --output prompt_enrichi.txt
```

### 3. Workflow complet (5 minutes)

```bash
# Créer la structure pour vos documents
mkdir -p data/documents/{regulations,eiopa,expert_papers}

# Ajouter vos propres documents (exemple)
python cli.py add-doc \
  --file "votre_reglement.pdf" \
  --type regulation_eu \
  --modules spread,equity \
  --title "Votre document" \
  --reliability 0.9

# Rechercher dans vos documents
python cli.py search --query "Article 180" --module spread

# Générer plusieurs prompts
for level in expert confirmed junior; do
  python cli.py generate \
    --ai claude-sonnet-4 \
    --level $level \
    --module spread \
    --output "prompt_${level}.txt"
done
```

## 📖 Guide d'utilisation

### Interface CLI

Le système dispose d'une interface ligne de commande complète :

```bash
# Voir toutes les options
python cli.py --help

# Commandes principales
python cli.py generate    # Générer un prompt
python cli.py add-doc     # Ajouter un document
python cli.py stats       # Statistiques
python cli.py search      # Rechercher
python cli.py health      # Diagnostic
python cli.py export      # Export des données
```

### Génération de Prompts

#### Paramètres Essentiels

```bash
python cli.py generate \
  --ai claude-sonnet-4 \          # IA cible
  --level expert \                 # Niveau d'expertise
  --module spread \                # Module SCR
  --language fr \                  # Langue (fr/en)
  --max-length 4000 \             # Longueur max (mots)
  --output mon_prompt.txt \       # Fichier de sortie
  --show-recommendations          # Afficher conseils d'usage
```

#### Niveaux d'Expertise

- **`junior`** : Explications simples, vocabulaire accessible
- **`confirmed`** : Niveau actuaire standard, formules détaillées
- **`expert`** : Références réglementaires précises, cas complexes
- **`regulation_specialist`** : Expertise ultra-technique, nuances réglementaires

#### IA Supportées

- **`claude-sonnet-4`** : ⭐ **Recommandé** pour documents techniques
- **`claude-opus-4`** : Pour analyses complexes
- **`gpt-4`** : Excellent pour structuration
- **`gpt-4-turbo`** : Version accélérée
- **`gemini-pro`** : Bon pour approche pédagogique

### Usage Programmatique

```python
from src.main import SCRPromptGenerator
from src.knowledge.models import PromptConfig
from src.config import AIProvider, ExpertiseLevel, SCRModule

# Initialisation
with SCRPromptGenerator() as generator:
    
    # Configuration du prompt
    config = PromptConfig(
        ai_provider=AIProvider.CLAUDE_SONNET_4,
        expertise_level=ExpertiseLevel.EXPERT,
        scr_module=SCRModule.SPREAD,
        max_length=3000,
        include_examples=True,
        include_formulas=True
    )
    
    # Génération
    result = generator.generate_optimized_prompt(config)
    
    if result['success']:
        print(f"Prompt: {result['prompt']}")
        print(f"Qualité: {result['quality_score']}")
        print(f"Sources: {result['metadata']['knowledge_base_stats']['relevant_documents']}")
```

## 📚 Gestion des documents

### Types de Documents Supportés

| Type | Description | Fiabilité | Exemples |
|------|-------------|-----------|----------|
| `regulation_eu` | Règlements européens | 1.0 | Règlement délégué (UE) 2015/35 |
| `directive` | Directives européennes | 0.95 | Directive 2009/138/CE |
| `eiopa_guidelines` | Guidelines EIOPA | 0.9 | Guidelines on spread risk |
| `technical_standards` | Standards techniques | 0.85 | ITS, RTS |
| `industry_paper` | Papers professionnels | 0.8 | Études Big 4, consultants |
| `academic_paper` | Papers académiques | 0.75 | Recherche universitaire |
| `internal_doc` | Documents internes | 0.6 | Méthodologies société |

### Ajout de Documents

#### Via CLI

```bash
# Document PDF local
python cli.py add-doc \
  --file "data/documents/reglement_2015_35.pdf" \
  --type regulation_eu \
  --modules spread,equity,interest_rate \
  --title "Règlement délégué (UE) 2015/35" \
  --reliability 1.0 \
  --language fr \
  --date 2015-01-17

# Document depuis URL
python cli.py add-doc \
  --file "https://eiopa.europa.eu/guidelines/spread-risk" \
  --type eiopa_guidelines \
  --modules spread \
  --title "EIOPA Guidelines on Spread Risk"
```

#### Via Script Python

```python
from src.main import SCRPromptGenerator
from src.config import DocumentType, SCRModule

with SCRPromptGenerator() as generator:
    success = generator.add_document_source(
        file_path_or_url="document.pdf",
        doc_type=DocumentType.REGULATION_EU,
        scr_modules=[SCRModule.SPREAD, SCRModule.EQUITY],
        title="Mon document",
        reliability_score=0.9,
        language="fr"
    )
```

#### Traitement en Lot

Créez un fichier `batch_config.yaml` :

```yaml
documents:
  - file_path: './data/documents/reglement_2015_35.pdf'
    doc_type: 'regulation_eu'
    scr_modules: ['spread', 'equity']
    metadata:
      title: 'Règlement délégué (UE) 2015/35'
      reliability_score: 1.0
      
  - file_path: 'https://eiopa.europa.eu/guidelines'
    doc_type: 'eiopa_guidelines'
    scr_modules: ['spread']
    metadata:
      title: 'EIOPA Guidelines'
```

Puis :
```bash
python cli.py batch --config batch_config.yaml
```

### Recherche et Exploration

```bash
# Recherche textuelle
python cli.py search --query "Article 180"

# Filtrage par module
python cli.py search --module spread --min-reliability 0.8

# Recherche avancée
python cli.py search \
  --query "facteur de stress" \
  --module spread \
  --type regulation_eu \
  --limit 5
```

## 🤖 IA supportées

### Configuration par IA

Chaque IA a des optimisations spécifiques :

#### Claude Sonnet 4 ⭐
- **Forces** : Documents techniques, raisonnement structuré
- **Template** : Sections détaillées, contexte étendu
- **Recommandations** : Idéal pour experts Solvabilité 2

#### GPT-4
- **Forces** : Structuration claire, précision technique
- **Template** : Format organisé, exemples concrets
- **Recommandations** : Bon pour formation et documentation

#### Gemini Pro
- **Forces** : Approche pédagogique, créativité
- **Template** : Formats variés, explications accessibles
- **Recommandations** : Parfait pour sensibilisation équipes

### Exemples de Prompts Générés

#### Pour Claude Expert (Spread) :
```
# CONTEXTE & EXPERTISE
Tu es un actuaire expert en Solvabilité 2 avec 15+ années d'expérience...

# SOURCES RÉGLEMENTAIRES PRIORITAIRES
- Règlement délégué (UE) 2015/35 (Articles: 175, 180, 181)
- EIOPA Guidelines on Spread Risk

# CONCEPTS CLÉS À COUVRIR
- Facteurs de stress par notation de crédit
- Duration modifiée et calcul de sensibilité
- Formule SCR_spread = SCR_bonds + SCR_securitisation + SCR_cd
...
```

#### Pour GPT-4 Confirmé (Equity) :
```
You are a Solvency II actuary with expertise in equity risk calculations.

OBJECTIVE: Create a comprehensive guide for equity SCR calculation.

REGULATORY FRAMEWORK:
- Commission Delegated Regulation (EU) 2015/35
- EIOPA Guidelines on equity risk

KEY REQUIREMENTS:
1. Type I vs Type II classification (39% vs 49%)
2. Symmetric adjustment mechanism
3. Long Term Equity Investment treatment
...
```

## 🎯 Modules SCR

### Modules Supportés

| Module | Description | Articles Clés | Exemples |
|--------|-------------|---------------|----------|
| `spread` | Risque de crédit/spread | 175-181 | Obligations, prêts, CDS |
| `interest_rate` | Risque de taux | 165-174 | Chocs haussier/baissier |
| `equity` | Risque actions | 154-164 | Type I/II, dampener |
| `currency` | Risque de change | 188-195 | Chocs par devise |
| `concentration` | Risque de concentration | 182-187 | Seuils par émetteur |
| `counterparty` | Risque de contrepartie | 189-214 | Réassurance, dérivés |
| `operational` | Risque opérationnel | 312-318 | 25% BSCR minimum |

### Spécificités par Module

#### SCR de Spread
```bash
# Génération spécialisée spread
python cli.py generate \
  --ai claude-sonnet-4 \
  --level expert \
  --module spread \
  --max-length 4000

# Recommandations automatiques :
# ✅ Vérifiez les facteurs avec révisions 2025
# 📊 Incluez exemples avec différentes notations
# 🔢 Validez corrélations spread/taux (50%→25%)
```

#### SCR Actions
```bash
# Spécialisation actions
python cli.py generate \
  --ai claude-sonnet-4 \
  --level expert \
  --module equity

# Points clés automatiques :
# - Type I (39%) vs Type II (49%)
# - Ajustement symétrique ±17%
# - LTEI et critères d'éligibilité
```

## 📊 Exemples concrets

### Cas d'Usage Réels

#### 1. Formation Équipe Junior

```bash
# Prompts pédagogiques
python cli.py generate --ai gemini-pro --level junior --module spread
python cli.py generate --ai gemini-pro --level junior --module equity

# Résultat : Explications simples avec exemples concrets
```

#### 2. Documentation Technique

```bash
# Documentation experte
python cli.py generate --ai claude-sonnet-4 --level expert --module spread --output doc_spread.txt
python cli.py generate --ai gpt-4 --level expert --module equity --output doc_equity.txt

# Résultat : Fiches techniques complètes avec références
```

#### 3. Audit et Contrôle

```bash
# Prompts pour validation
python cli.py generate \
  --ai claude-sonnet-4 \
  --level regulation_specialist \
  --module spread \
  --output audit_spread.txt

# Résultat : Focus sur conformité réglementaire
```

### Métriques de Performance

```bash
# Statistiques détaillées
python cli.py stats --detailed

# Résultat typique :
# 📊 STATISTIQUES SCR PROMPT GENERATOR
# ====================================
# 📄 Base de connaissances:
#    • Total documents: 15
#    • Base de données: 2.4 MB
# 
# 📑 Documents par type:
#    • regulation_eu: 3
#    • eiopa_guidelines: 5
#    • expert_papers: 7
# 
# 🎯 Documents par module SCR:
#    • spread: 8
#    • equity: 6
#    • interest_rate: 4
```

### Comparaison Avant/Après

#### Prompt Standard (manuel)
```
Explique-moi le calcul du SCR de spread selon Solvabilité 2
```

#### Prompt Optimisé (généré)
```
# CONTEXTE & EXPERTISE
Tu es un actuaire expert en Solvabilité 2 avec 15+ années d'expérience 
dans le calcul des SCR. Tu maîtrises parfaitement le Règlement délégué (UE) 2015/35.

# MISSION
Créer une fiche technique sur le calcul du SCR de spread sous Solvabilité 2,
destinée à des actuaires confirmés.

# SOURCES RÉGLEMENTAIRES PRIORITAIRES
1. **Règlement délégué (UE) 2015/35** (Articles: 175, 180, 181)
2. **EIOPA Guidelines on Spread Risk** (Fiabilité: 0.9/1.0)

# CONCEPTS CLÉS À COUVRIR
- Facteurs de stress par notation de crédit (AAA à Non noté)
- Duration modifiée et calcul de sensibilité aux spreads
- Formule SCR_spread = SCR_bonds + SCR_securitisation + SCR_cd
- Corrélations avec autres modules (taux, actions)

# STRUCTURE OBLIGATOIRE
### 1. SYNTHÈSE EXÉCUTIVE
### 2. CADRE RÉGLEMENTAIRE
### 3. MÉTHODOLOGIE DE CALCUL
### 4. EXEMPLES PRATIQUES
### 5. POINTS D'ATTENTION

# EXEMPLES CONCRETS REQUIS
Obligation BBB 100M€, duration 8 ans → SCR = 100M€ × 8 × 2.5% = 20M€

**RENDU :** Document de 3000 mots, niveau technique professionnel.
```

**Résultat :** 10x plus de détails techniques pertinents !

## 🔧 Configuration avancée

### Personnalisation des Templates

```python
# Ajouter un template personnalisé
from src.prompts.templates import PromptTemplateLibrary, PromptTemplate

library = PromptTemplateLibrary()

custom_template = PromptTemplate(
    name="custom_expert_fr",
    content="""
    Contexte spécifique à votre organisation...
    {custom_requirements}
    """,
    variables=["custom_requirements"]
)

library.add_template(custom_template)
```

### Configuration Base de Données

```python
# Configuration avancée
from src.config import Config

# Modification des paramètres
Config.MAX_FILE_SIZE_MB = 200  # Fichiers plus volumineux
Config.DEFAULT_DB_PATH = "/custom/path/scr.db"
Config.LOG_LEVEL = "DEBUG"
```

### Export/Import

```bash
# Export de la base complète
python cli.py export --output backup.json --format json

# Export CSV pour analyse
python cli.py export --output data.csv --format csv

# Import (via script Python)
python restore_backup.py backup.json
```

## 🧪 Tests

### Tests Automatisés

```bash
# Tests unitaires
python -m pytest tests/ -v

# Test de performance
python test_performance.py

# Test complet du système
python test_complete_system.py
```

### Tests Manuels

```bash
# Test rapide (30s)
python run_tests.py quick

# Test avec documents (2min)
python run_tests.py document

# Test comparatif multi-IA (5min)
python run_tests.py multi

# Test interactif
python run_tests.py interactive
```

### Validation Continue

```bash
# Health check quotidien
python cli.py health --fix

# Validation de la qualité des prompts
python validate_prompt_quality.py

# Statistiques d'usage
python cli.py stats --export daily_stats.json
```

## 📈 Performance

### Métriques Typiques

- **Génération prompt** : < 3 secondes
- **Ajout document PDF** : 10-30 secondes
- **Recherche base** : < 1 seconde
- **Mémoire utilisée** : 50-200 MB

### Optimisations

#### Base de Données
```bash
# Nettoyage périodique
python -c "
from src.main import SCRPromptGenerator
with SCRPromptGenerator() as gen:
    gen.cleanup_old_data(days_threshold=90)
"
```

#### Cache et Index
```sql
-- Optimisations SQLite (automatiques)
CREATE INDEX idx_documents_module ON documents(scr_modules);
CREATE INDEX idx_concepts_module ON scr_concepts(scr_module);
```

### Monitoring

```bash
# Logs détaillés
tail -f logs/scr_generator_$(date +%Y%m%d).log

# Métriques système
python cli.py health --detailed
```

## 🤝 Contribution

### Pour contribuer au projet :

1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/amazing`)
3. **Commiter** vos changements (`git commit -m 'Add amazing feature'`)
4. **Pusher** sur la branche (`git push origin feature/amazing`)
5. **Ouvrir** une Pull Request

### Standards de Code

```bash
# Formatage
black src/ tests/

# Linting
flake8 src/

# Type checking
mypy src/

# Tests
pytest tests/ --cov=src/
```

### Roadmap

- [ ] **Support GPT-5** et futurs modèles
- [ ] **Interface web** avec Streamlit
- [ ] **Intégration APIs** IA directes
- [ ] **Module ORSA** et Pilier 2
- [ ] **Support multilingue** (DE, IT, ES)
- [ ] **Plugin Excel** pour actuaires

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🆘 Support et Contact

### Documentation
- **README** : Guide complet (ce document)
- **Code documentation** : Docstrings intégrées
- **Examples** : Dossier `examples/`

### Support Technique
- **Issues** : Utilisez GitHub Issues
- **Tests** : `python run_tests.py --help`
- **Health check** : `python cli.py health`

### Communauté
- **Actuaires** : Partagez vos templates et documents
- **Développeurs** : Contribuez aux parsers et optimisations
- **Experts réglementaires** : Validez et enrichissez les contenus

---

**Fait avec ❤️ pour la communauté actuarielle et Solvabilité 2**

> "Transformez vos connaissances réglementaires en prompts d'experts"