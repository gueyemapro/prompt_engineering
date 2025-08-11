# ==========================================
# ÉTAPE 2 : MODÈLES DE DONNÉES ET CONFIGURATION
# Fichier: src/config/settings.py
# ==========================================

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, date


# Configuration globale
class Config:
    """Configuration globale de l'application"""

    # Base de données
    DEFAULT_DB_PATH = "./data/scr_knowledge.db"

    # Répertoires
    DATA_DIR = "./data"
    DOCUMENTS_DIR = "./data/documents"
    LOGS_DIR = "./logs"

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Paramètres de parsing
    MAX_FILE_SIZE_MB = 100
    SUPPORTED_LANGUAGES = ["fr", "en"]

    # IA et prompts
    DEFAULT_AI_PROVIDER = "claude-sonnet-4"
    DEFAULT_EXPERTISE_LEVEL = "expert"
    DEFAULT_MAX_PROMPT_LENGTH = 3000


# Énumérations
class AIProvider(Enum):
    """Fournisseurs d'IA supportés"""
    CLAUDE_SONNET_4 = "claude-sonnet-4"
    CLAUDE_OPUS_4 = "claude-opus-4"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GEMINI_PRO = "gemini-pro"


class ExpertiseLevel(Enum):
    """Niveaux d'expertise pour les prompts"""
    JUNIOR = "junior"
    CONFIRMED = "confirmed"
    EXPERT = "expert"
    REGULATION_SPECIALIST = "regulation_specialist"


class SCRModule(Enum):
    """Modules SCR de Solvabilité 2"""
    SPREAD = "spread"
    INTEREST_RATE = "interest_rate"
    EQUITY = "equity"
    CURRENCY = "currency"
    CONCENTRATION = "concentration"
    MARKET_GLOBAL = "market_global"
    COUNTERPARTY = "counterparty"
    OPERATIONAL = "operational"
    LIFE = "life"
    NON_LIFE = "non_life"


class DocumentType(Enum):
    """Types de documents sources"""
    REGULATION_EU = "regulation_eu"
    DIRECTIVE = "directive"
    EIOPA_GUIDELINES = "eiopa_guidelines"
    TECHNICAL_STANDARDS = "technical_standards"
    INDUSTRY_PAPER = "industry_paper"
    INTERNAL_DOC = "internal_doc"
    ACADEMIC_PAPER = "academic_paper"


# ==========================================
# Fichier: src/knowledge/models.py
# ==========================================

@dataclass
class DocumentSource:
    """Modèle pour un document source"""
    id: str
    title: str
    doc_type: DocumentType
    url: Optional[str] = None
    file_path: Optional[str] = None
    publication_date: Optional[date] = None
    regulatory_articles: List[str] = None
    scr_modules: List[SCRModule] = None
    language: str = "fr"
    reliability_score: float = 0.8  # 0-1
    last_updated: datetime = None
    content_hash: str = ""

    def __post_init__(self):
        """Post-traitement après initialisation"""
        if self.regulatory_articles is None:
            self.regulatory_articles = []
        if self.scr_modules is None:
            self.scr_modules = []
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class SCRConcept:
    """Modèle pour un concept SCR"""
    id: Optional[int] = None
    concept_name: str = ""
    scr_module: SCRModule = SCRModule.SPREAD
    definition: str = ""
    formula: Optional[str] = None
    regulatory_article: Optional[str] = None
    source_document_id: Optional[str] = None
    examples: List[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class PromptConfig:
    """Configuration pour la génération de prompts"""
    ai_provider: AIProvider
    expertise_level: ExpertiseLevel
    scr_module: SCRModule
    language: str = "fr"
    output_format: str = "technical_sheet"
    include_examples: bool = True
    include_formulas: bool = True
    max_length: int = 3000
    custom_requirements: Optional[List[str]] = None

    def __post_init__(self):
        if self.custom_requirements is None:
            self.custom_requirements = []


#



# ==========================================
# INSTRUCTIONS POUR L'ÉTAPE 2
# ==========================================

"""
CRÉER LES FICHIERS SUIVANTS:

1. src/config/settings.py
   - Copiez la section "Configuration globale" + "Énumérations"

2. src/knowledge/models.py  
   - Copiez la section "Modèles de données"

3. src/config/__init__.py
   - Copiez la section "Configuration package"

4. src/knowledge/__init__.py
   - Copiez la section "Knowledge management package"

TESTER L'INSTALLATION:
```bash
cd scr_prompt_generator
python -c "from src.config import Config, SCRModule; print('✅ Configuration OK')"
python -c "from src.knowledge import DocumentSource; print('✅ Modèles OK')"
```

Si tout fonctionne, vous êtes prêt pour l'ÉTAPE 3 !
"""