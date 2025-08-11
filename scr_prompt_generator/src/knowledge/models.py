# ==========================================
# MODÈLES DE DONNÉES COMPLETS
# Fichier: src/knowledge/models.py
# ==========================================

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import json

# Import des enums depuis config
from ..config import DocumentType, SCRModule, AIProvider, ExpertiseLevel


# ==========================================
# MODÈLES PRINCIPAUX
# ==========================================

@dataclass
class DocumentSource:
    """
    Modèle pour représenter un document source réglementaire

    Attributes:
        id: Identifiant unique du document
        title: Titre du document
        doc_type: Type de document (règlement, directive, etc.)
        url: URL source du document (optionnel)
        file_path: Chemin local du fichier (optionnel)
        publication_date: Date de publication (optionnel)
        regulatory_articles: Liste des articles réglementaires mentionnés
        scr_modules: Liste des modules SCR concernés
        language: Langue du document
        reliability_score: Score de fiabilité (0-1)
        last_updated: Dernière mise à jour
        content_hash: Hash du contenu pour détecter les changements
        metadata: Métadonnées additionnelles
    """
    id: str
    title: str
    doc_type: DocumentType
    url: Optional[str] = None
    file_path: Optional[str] = None
    publication_date: Optional[date] = None
    regulatory_articles: List[str] = field(default_factory=list)
    scr_modules: List[SCRModule] = field(default_factory=list)
    language: str = "fr"
    reliability_score: float = 0.8
    last_updated: datetime = field(default_factory=datetime.now)
    content_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-traitement après initialisation"""
        # Validation du score de fiabilité
        if not 0 <= self.reliability_score <= 1:
            raise ValueError("reliability_score doit être entre 0 et 1")

        # Validation de la langue
        if self.language not in ["fr", "en", "de", "es", "it"]:
            self.language = "fr"  # Valeur par défaut

    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour sérialisation"""
        return {
            'id': self.id,
            'title': self.title,
            'doc_type': self.doc_type.value,
            'url': self.url,
            'file_path': self.file_path,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'regulatory_articles': self.regulatory_articles,
            'scr_modules': [m.value for m in self.scr_modules],
            'language': self.language,
            'reliability_score': self.reliability_score,
            'last_updated': self.last_updated.isoformat(),
            'content_hash': self.content_hash,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentSource':
        """Création depuis un dictionnaire"""
        # Conversion des dates
        pub_date = None
        if data.get('publication_date'):
            pub_date = datetime.fromisoformat(data['publication_date']).date()

        last_updated = datetime.now()
        if data.get('last_updated'):
            last_updated = datetime.fromisoformat(data['last_updated'])

        return cls(
            id=data['id'],
            title=data['title'],
            doc_type=DocumentType(data['doc_type']),
            url=data.get('url'),
            file_path=data.get('file_path'),
            publication_date=pub_date,
            regulatory_articles=data.get('regulatory_articles', []),
            scr_modules=[SCRModule(m) for m in data.get('scr_modules', [])],
            language=data.get('language', 'fr'),
            reliability_score=data.get('reliability_score', 0.8),
            last_updated=last_updated,
            content_hash=data.get('content_hash', ''),
            metadata=data.get('metadata', {})
        )

    def add_regulatory_article(self, article: str):
        """Ajouter un article réglementaire"""
        if article not in self.regulatory_articles:
            self.regulatory_articles.append(article)

    def add_scr_module(self, module: SCRModule):
        """Ajouter un module SCR"""
        if module not in self.scr_modules:
            self.scr_modules.append(module)

    def is_relevant_for_module(self, module: SCRModule) -> bool:
        """Vérifier si le document est pertinent pour un module SCR"""
        return module in self.scr_modules


@dataclass
class SCRConcept:
    """
    Modèle pour représenter un concept SCR

    Attributes:
        id: Identifiant unique (auto-généré)
        concept_name: Nom du concept
        scr_module: Module SCR concerné
        definition: Définition du concept
        formula: Formule mathématique (optionnel)
        regulatory_article: Article réglementaire de référence
        source_document_id: ID du document source
        examples: Liste d'exemples
        tags: Tags pour classification
        created_at: Date de création
        updated_at: Date de dernière modification
        confidence_score: Score de confiance de l'extraction (0-1)
    """
    concept_name: str
    scr_module: SCRModule
    definition: str
    id: Optional[int] = None
    formula: Optional[str] = None
    regulatory_article: Optional[str] = None
    source_document_id: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.8

    def __post_init__(self):
        """Post-traitement après initialisation"""
        # Validation du score de confiance
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("confidence_score doit être entre 0 et 1")

        # Nettoyage du nom du concept
        self.concept_name = self.concept_name.strip()
        if len(self.concept_name) < 3:
            raise ValueError("concept_name doit faire au moins 3 caractères")

    def add_example(self, example: str):
        """Ajouter un exemple"""
        if example.strip() and example not in self.examples:
            self.examples.append(example.strip())
            self.updated_at = datetime.now()

    def add_tag(self, tag: str):
        """Ajouter un tag"""
        if tag.strip() and tag not in self.tags:
            self.tags.append(tag.strip().lower())

    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'id': self.id,
            'concept_name': self.concept_name,
            'scr_module': self.scr_module.value,
            'definition': self.definition,
            'formula': self.formula,
            'regulatory_article': self.regulatory_article,
            'source_document_id': self.source_document_id,
            'examples': self.examples,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence_score': self.confidence_score
        }


@dataclass
class PromptConfig:
    """
    Configuration pour la génération de prompts

    Attributes:
        ai_provider: Fournisseur d'IA cible
        expertise_level: Niveau d'expertise de l'utilisateur
        scr_module: Module SCR à traiter
        language: Langue de génération
        output_format: Format de sortie désiré
        include_examples: Inclure des exemples
        include_formulas: Inclure des formules mathématiques
        include_regulatory_refs: Inclure les références réglementaires
        max_length: Longueur maximale en mots
        custom_requirements: Exigences personnalisées
        context_level: Niveau de contexte à inclure
        technical_depth: Profondeur technique (1-5)
    """
    ai_provider: AIProvider
    expertise_level: ExpertiseLevel
    scr_module: SCRModule
    language: str = "fr"
    output_format: str = "technical_sheet"
    include_examples: bool = True
    include_formulas: bool = True
    include_regulatory_refs: bool = True
    max_length: int = 3000
    custom_requirements: List[str] = field(default_factory=list)
    context_level: str = "high"  # low, medium, high
    technical_depth: int = 3  # 1-5

    def __post_init__(self):
        """Post-traitement après initialisation"""
        # Validation de la profondeur technique
        if not 1 <= self.technical_depth <= 5:
            self.technical_depth = 3

        # Validation du niveau de contexte
        if self.context_level not in ["low", "medium", "high"]:
            self.context_level = "high"

        # Validation de la longueur
        if self.max_length < 500:
            self.max_length = 500
        elif self.max_length > 10000:
            self.max_length = 10000

    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'ai_provider': self.ai_provider.value,
            'expertise_level': self.expertise_level.value,
            'scr_module': self.scr_module.value,
            'language': self.language,
            'output_format': self.output_format,
            'include_examples': self.include_examples,
            'include_formulas': self.include_formulas,
            'include_regulatory_refs': self.include_regulatory_refs,
            'max_length': self.max_length,
            'custom_requirements': self.custom_requirements,
            'context_level': self.context_level,
            'technical_depth': self.technical_depth
        }

    def get_complexity_score(self) -> float:
        """Calcul du score de complexité (0-1)"""
        score = 0.0

        # Contribution du niveau d'expertise
        expertise_scores = {
            ExpertiseLevel.JUNIOR: 0.2,
            ExpertiseLevel.CONFIRMED: 0.5,
            ExpertiseLevel.EXPERT: 0.8,
            ExpertiseLevel.REGULATION_SPECIALIST: 1.0
        }
        score += expertise_scores.get(self.expertise_level, 0.5) * 0.4

        # Contribution de la profondeur technique
        score += (self.technical_depth / 5) * 0.3

        # Contribution du niveau de contexte
        context_scores = {"low": 0.2, "medium": 0.5, "high": 0.8}
        score += context_scores.get(self.context_level, 0.5) * 0.2

        # Contribution des options
        if self.include_formulas:
            score += 0.05
        if self.include_examples:
            score += 0.03
        if self.custom_requirements:
            score += 0.02

        return min(score, 1.0)


# ==========================================
# MODÈLES UTILITAIRES
# ==========================================

@dataclass
class PromptGenerationResult:
    """
    Résultat de génération de prompt avec métadonnées

    Attributes:
        prompt: Contenu du prompt généré
        config: Configuration utilisée
        metadata: Métadonnées de génération
        success: Succès de la génération
        error_message: Message d'erreur si échec
        generation_time: Temps de génération en secondes
        quality_score: Score de qualité estimé (0-1)
        usage_recommendations: Recommandations d'utilisation
    """
    prompt: str
    config: PromptConfig
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None
    generation_time: float = 0.0
    quality_score: float = 0.8
    usage_recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour export"""
        return {
            'prompt': self.prompt,
            'config': self.config.to_dict(),
            'metadata': self.metadata,
            'success': self.success,
            'error_message': self.error_message,
            'generation_time': self.generation_time,
            'quality_score': self.quality_score,
            'usage_recommendations': self.usage_recommendations
        }

    def save_to_file(self, filepath: str, include_metadata: bool = True):
        """Sauvegarde du prompt dans un fichier"""
        content = self.prompt

        if include_metadata and self.success:
            content += f"\n\n{'=' * 60}\n"
            content += f"MÉTADONNÉES DE GÉNÉRATION\n"
            content += f"{'=' * 60}\n"
            content += f"IA: {self.config.ai_provider.value}\n"
            content += f"Niveau: {self.config.expertise_level.value}\n"
            content += f"Module: {self.config.scr_module.value}\n"
            content += f"Temps génération: {self.generation_time:.3f}s\n"
            content += f"Score qualité: {self.quality_score:.2f}\n"

            if self.usage_recommendations:
                content += f"\nRecommandations:\n"
                for rec in self.usage_recommendations:
                    content += f"- {rec}\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


@dataclass
class DocumentProcessingResult:
    """
    Résultat du traitement d'un document

    Attributes:
        document_source: DocumentSource créé
        success: Succès du traitement
        extracted_concepts: Concepts extraits automatiquement
        processing_time: Temps de traitement
        warnings: Avertissements éventuels
        error_message: Message d'erreur si échec
    """
    document_source: Optional[DocumentSource]
    success: bool
    extracted_concepts: List[SCRConcept] = field(default_factory=list)
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def add_warning(self, warning: str):
        """Ajouter un avertissement"""
        if warning not in self.warnings:
            self.warnings.append(warning)

    def get_summary(self) -> Dict[str, Any]:
        """Résumé du traitement"""
        return {
            'success': self.success,
            'document_id': self.document_source.id if self.document_source else None,
            'concepts_extracted': len(self.extracted_concepts),
            'processing_time': self.processing_time,
            'warnings_count': len(self.warnings),
            'has_errors': bool(self.error_message)
        }


# ==========================================
# MODÈLES DE RECHERCHE ET FILTRAGE
# ==========================================

@dataclass
class SearchCriteria:
    """
    Critères de recherche dans la base de connaissances

    Attributes:
        scr_modules: Modules SCR à inclure
        document_types: Types de documents
        min_reliability: Score de fiabilité minimum
        language: Langue des documents
        date_from: Date de début
        date_to: Date de fin
        keywords: Mots-clés à rechercher
        regulatory_articles: Articles réglementaires spécifiques
    """
    scr_modules: List[SCRModule] = field(default_factory=list)
    document_types: List[DocumentType] = field(default_factory=list)
    min_reliability: float = 0.0
    language: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    keywords: List[str] = field(default_factory=list)
    regulatory_articles: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Vérifier si les critères sont vides"""
        return (not self.scr_modules and
                not self.document_types and
                self.min_reliability == 0.0 and
                not self.language and
                not self.date_from and
                not self.date_to and
                not self.keywords and
                not self.regulatory_articles)


@dataclass
class KnowledgeBaseStats:
    """
    Statistiques de la base de connaissances

    Attributes:
        total_documents: Nombre total de documents
        total_concepts: Nombre total de concepts
        documents_by_type: Répartition par type de document
        documents_by_module: Répartition par module SCR
        concepts_by_module: Répartition des concepts par module
        average_reliability: Fiabilité moyenne
        languages: Langues représentées
        date_range: Plage de dates des documents
        database_size_mb: Taille de la base en MB
        last_update: Dernière mise à jour
    """
    total_documents: int = 0
    total_concepts: int = 0
    documents_by_type: Dict[str, int] = field(default_factory=dict)
    documents_by_module: Dict[str, int] = field(default_factory=dict)
    concepts_by_module: Dict[str, int] = field(default_factory=dict)
    average_reliability: float = 0.0
    languages: List[str] = field(default_factory=list)
    date_range: Dict[str, Optional[date]] = field(default_factory=dict)
    database_size_mb: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'total_documents': self.total_documents,
            'total_concepts': self.total_concepts,
            'documents_by_type': self.documents_by_type,
            'documents_by_module': self.documents_by_module,
            'concepts_by_module': self.concepts_by_module,
            'average_reliability': self.average_reliability,
            'languages': self.languages,
            'date_range': {
                'earliest': self.date_range.get('earliest').isoformat() if self.date_range.get('earliest') else None,
                'latest': self.date_range.get('latest').isoformat() if self.date_range.get('latest') else None
            },
            'database_size_mb': self.database_size_mb,
            'last_update': self.last_update.isoformat()
        }


# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def create_document_id(title: str, content_hash: str, doc_type: DocumentType) -> str:
    """
    Création d'un ID unique pour un document

    Args:
        title: Titre du document
        content_hash: Hash du contenu
        doc_type: Type de document

    Returns:
        ID unique
    """
    import re

    # Nettoyage du titre
    clean_title = re.sub(r'[^\w\s-]', '', title.lower())
    clean_title = re.sub(r'\s+', '_', clean_title)[:30]

    return f"{doc_type.value}_{clean_title}_{content_hash[:8]}"


def validate_regulatory_article(article: str) -> bool:
    """
    Validation d'un numéro d'article réglementaire

    Args:
        article: Numéro d'article à valider

    Returns:
        True si valide
    """
    import re

    # Patterns d'articles valides
    patterns = [
        r'^\d+[a-z]?$',  # 180, 180a
        r'^\d+/\d+$',  # 2015/35
        r'^\d+/\d+/CE$',  # 2009/138/CE
    ]

    return any(re.match(pattern, article) for pattern in patterns)


def estimate_reading_time(text: str) -> int:
    """
    Estimation du temps de lecture en minutes

    Args:
        text: Texte à analyser

    Returns:
        Temps de lecture estimé en minutes
    """
    words_count = len(text.split())
    words_per_minute = 200  # Vitesse de lecture moyenne
    return max(1, words_count // words_per_minute)


def calculate_prompt_complexity(config: PromptConfig, kb_stats: KnowledgeBaseStats) -> float:
    """
    Calcul de la complexité d'un prompt

    Args:
        config: Configuration du prompt
        kb_stats: Statistiques de la base

    Returns:
        Score de complexité (0-1)
    """
    complexity = config.get_complexity_score()

    # Ajustement selon les données disponibles
    module_docs = kb_stats.documents_by_module.get(config.scr_module.value, 0)
    if module_docs == 0:
        complexity *= 0.7  # Réduction si pas de données
    elif module_docs > 5:
        complexity *= 1.1  # Augmentation si beaucoup de données

    return min(complexity, 1.0)


# ==========================================
# EXPORTS
# ==========================================

__all__ = [
    'DocumentSource',
    'SCRConcept',
    'PromptConfig',
    'PromptGenerationResult',
    'DocumentProcessingResult',
    'SearchCriteria',
    'KnowledgeBaseStats',
    'create_document_id',
    'validate_regulatory_article',
    'estimate_reading_time',
    'calculate_prompt_complexity'
]