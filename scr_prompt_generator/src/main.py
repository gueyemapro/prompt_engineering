# ==========================================
# ORCHESTRATEUR PRINCIPAL - src/main.py
# SCR Prompt Generator - Fichier principal
# ==========================================

import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .config import Config, DocumentType, SCRModule, AIProvider, ExpertiseLevel
from .knowledge.database import SCRKnowledgeBase
from .knowledge.models import DocumentSource, PromptConfig, SCRConcept
from .parsers import create_parser
from .prompts.generator import PromptEngineer


class SCRPromptGenerator:
    """
    Orchestrateur principal du système de génération de prompts SCR

    Cette classe coordonne tous les composants :
    - Base de connaissances (documents et concepts SCR)
    - Parsers de documents (PDF, HTML)
    - Générateur de prompts optimisés
    - Gestion des statistiques et métadonnées
    """

    def __init__(self, data_dir: str = None, db_path: str = None):
        """
        Initialisation du générateur

        Args:
            data_dir: Répertoire de données (optionnel, utilise Config.DATA_DIR par défaut)
            db_path: Chemin base de données (optionnel, utilise Config.DEFAULT_DB_PATH par défaut)
        """
        # Configuration des chemins
        self.data_dir = Path(data_dir or Config.DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.documents_dir = self.data_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)

        # Configuration du logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

        # Initialisation des composants principaux
        self.knowledge_base = SCRKnowledgeBase(db_path or Config.DEFAULT_DB_PATH)
        self.prompt_engineer = PromptEngineer(self.knowledge_base)

        # Compteurs et statistiques
        self._documents_processed = 0
        self._prompts_generated = 0
        self._startup_time = datetime.now()

        self.logger.info("SCR Prompt Generator initialisé avec succès")
        self.logger.info(f"Répertoire de données: {self.data_dir}")
        self.logger.info(f"Base de données: {self.knowledge_base.db_path}")

    def _setup_logging(self):
        """Configuration du système de logging"""
        logs_dir = Path(Config.LOGS_DIR)
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"scr_generator_{datetime.now().strftime('%Y%m%d')}.log"

        # Configuration des handlers
        handlers = [
            logging.StreamHandler(),  # Console
            logging.FileHandler(log_file, encoding='utf-8')  # Fichier
        ]

        # Configuration du logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT,
            handlers=handlers
        )

        # Suppression des logs trop verbeux
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)

    def add_document_source(self,
                            file_path_or_url: str,
                            doc_type: DocumentType,
                            scr_modules: List[SCRModule],
                            **metadata) -> bool:
        """
        Ajout et traitement d'un nouveau document source

        Args:
            file_path_or_url: Chemin fichier local ou URL
            doc_type: Type de document (regulation_eu, eiopa_guidelines, etc.)
            scr_modules: Liste des modules SCR concernés par ce document
            **metadata: Métadonnées additionnelles (title, url, reliability_score, etc.)

        Returns:
            True si l'ajout et le traitement ont réussi, False sinon
        """
        try:
            self.logger.info(f"Début traitement document: {file_path_or_url}")

            # 1. Vérification de la taille du fichier (si fichier local)
            if not file_path_or_url.startswith(('http://', 'https://')):
                file_path = Path(file_path_or_url)
                if file_path.exists():
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    if file_size_mb > Config.MAX_FILE_SIZE_MB:
                        self.logger.warning(f"Fichier volumineux ({file_size_mb:.1f}MB), traitement partiel possible")

            # 2. Parsing du document avec le parser approprié
            parser = create_parser(file_path_or_url)
            self.logger.debug(f"Parser sélectionné: {type(parser).__name__}")

            content_data = parser.extract_content(file_path_or_url)

            if not content_data.get('text_content'):
                self.logger.warning(f"Aucun contenu textuel extrait de {file_path_or_url}")
                return False

            # 3. Calcul du hash pour détection des changements
            text_content = content_data['text_content']
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()

            # 4. Extraction automatique des articles réglementaires
            regulatory_articles = parser.extract_regulatory_articles(text_content)
            self.logger.debug(f"Articles extraits: {regulatory_articles}")

            # 5. Génération de l'ID unique du document
            source_name = self._extract_source_name(file_path_or_url)
            doc_id = f"{doc_type.value}_{source_name}_{content_hash[:8]}"

            # 6. Extraction du titre intelligent
            title = metadata.get('title') or self._extract_title(content_data, file_path_or_url)

            # 7. Création de l'objet DocumentSource
            doc_source = DocumentSource(
                id=doc_id,
                title=title,
                doc_type=doc_type,
                url=file_path_or_url if file_path_or_url.startswith('http') else metadata.get('url'),
                file_path=file_path_or_url if not file_path_or_url.startswith('http') else None,
                publication_date=metadata.get('publication_date'),
                regulatory_articles=regulatory_articles,
                scr_modules=scr_modules,
                language=metadata.get('language', self._detect_language(text_content)),
                reliability_score=metadata.get('reliability_score',
                                               self._calculate_reliability_score(content_data, doc_type)),
                content_hash=content_hash,
                metadata=self._extract_additional_metadata(content_data)
            )

            # 8. Sauvegarde dans la base de connaissances
            success = self.knowledge_base.add_document(doc_source)

            if success:
                self.logger.info(f"Document ajouté avec succès: {doc_id}")
                self._documents_processed += 1

                # 9. Extraction automatique des concepts SCR
                extracted_concepts = self._auto_extract_concepts(doc_source, text_content)
                self.logger.info(f"Concepts extraits automatiquement: {len(extracted_concepts)}")

                return True
            else:
                self.logger.error(f"Échec sauvegarde document: {doc_id}")
                return False

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de {file_path_or_url}: {e}")
            self.logger.debug("Détails de l'erreur:", exc_info=True)
            return False

    def _extract_source_name(self, file_path_or_url: str) -> str:
        """Extraction du nom de source pour l'ID"""
        if file_path_or_url.startswith(('http://', 'https://')):
            # Pour les URLs, extraire le domaine
            from urllib.parse import urlparse
            parsed = urlparse(file_path_or_url)
            domain = parsed.netloc.replace('www.', '')
            return domain.replace('.', '_')[:20]
        else:
            # Pour les fichiers locaux, utiliser le nom sans extension
            return Path(file_path_or_url).stem[:20]

    def _extract_title(self, content_data: Dict[str, Any], source: str) -> str:
        """Extraction intelligente du titre depuis le contenu"""
        # 1. Priorité aux métadonnées du document
        if 'metadata' in content_data and content_data['metadata'].get('title'):
            title = content_data['metadata']['title'].strip()
            if len(title) > 5:
                return title

        # 2. Extraction depuis le contenu textuel
        text_content = content_data.get('text_content', '')
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]

        # Recherche de lignes candidates (titre probable)
        for line in lines[:15]:  # 15 premières lignes
            if 10 <= len(line) <= 200:  # Taille raisonnable pour un titre
                # Mots-clés indicateurs de titre SCR/réglementaire
                title_keywords = [
                    'règlement', 'directive', 'scr', 'solvabilité', 'solvency',
                    'eiopa', 'guidelines', 'article', 'commission', 'délégué'
                ]

                if any(keyword in line.lower() for keyword in title_keywords):
                    return line

        # 3. Titre par défaut basé sur la source
        if source.startswith(('http://', 'https://')):
            return f"Document web - {self._extract_source_name(source)}"
        else:
            return f"Document - {Path(source).stem}"

    def _detect_language(self, text_content: str) -> str:
        """Détection basique de la langue du document"""
        # Mots indicateurs par langue
        french_indicators = ['règlement', 'solvabilité', 'assurance', 'société', 'européenne']
        english_indicators = ['regulation', 'solvency', 'insurance', 'european', 'commission']

        text_lower = text_content.lower()

        french_count = sum(1 for word in french_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)

        if french_count > english_count:
            return 'fr'
        elif english_count > french_count:
            return 'en'
        else:
            return 'fr'  # Défaut français

    def _calculate_reliability_score(self, content_data: Dict[str, Any], doc_type: DocumentType) -> float:
        """Calcul automatique du score de fiabilité"""
        score = 0.5  # Base

        # Bonus selon le type de document
        type_scores = {
            DocumentType.REGULATION_EU: 1.0,
            DocumentType.DIRECTIVE: 0.95,
            DocumentType.EIOPA_GUIDELINES: 0.9,
            DocumentType.TECHNICAL_STANDARDS: 0.85,
            DocumentType.INDUSTRY_PAPER: 0.7,
            DocumentType.INTERNAL_DOC: 0.6,
            DocumentType.ACADEMIC_PAPER: 0.75
        }

        score = type_scores.get(doc_type, 0.5)

        # Ajustements selon le contenu
        text_content = content_data.get('text_content', '')

        # Bonus si beaucoup de références réglementaires
        article_count = len([word for word in text_content.split() if 'article' in word.lower()])
        if article_count > 10:
            score += 0.1

        # Bonus si contenu substantiel
        word_count = len(text_content.split())
        if word_count > 5000:
            score += 0.05
        elif word_count < 500:
            score -= 0.1

        # Plafonnement
        return min(max(score, 0.1), 1.0)

    def _extract_additional_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extraction de métadonnées additionnelles"""
        metadata = {}

        # Statistiques de contenu
        text_content = content_data.get('text_content', '')
        metadata['word_count'] = len(text_content.split())
        metadata['char_count'] = len(text_content)

        # Métadonnées du parser
        if 'statistics' in content_data:
            metadata.update(content_data['statistics'])

        # Informations sur le fichier source
        if 'file_info' in content_data:
            metadata['file_info'] = content_data['file_info']

        # Date de traitement
        metadata['processed_at'] = datetime.now().isoformat()

        return metadata

    def _auto_extract_concepts(self, doc_source: DocumentSource, content: str) -> List[SCRConcept]:
        """
        Extraction automatique simplifiée de concepts SCR

        Args:
            doc_source: Document source
            content: Contenu textuel du document

        Returns:
            Liste des concepts extraits
        """
        import re

        extracted_concepts = []

        # Patterns pour identifier des concepts SCR
        concept_patterns = [
            # Formules SCR
            (r'SCR[_\s]*(\w+)\s*=\s*([^.\n]{10,100})', 'Formule SCR'),

            # Facteurs et coefficients
            (r'([Ff]acteur[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Facteur'),
            (r'([Cc]oefficient[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Coefficient'),

            # Duration et sensibilité
            (r'([Dd]uration[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Duration'),
            (r'([Ss]ensibilité[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Sensibilité'),

            # Notations et ratings
            (r'([Nn]otation[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Notation'),
            (r'([Rr]ating[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Rating'),

            # Chocs et stress
            (r'([Cc]hoc[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Choc'),
            (r'([Ss]tress[^:]{0,30})\s*[:\-]\s*([^.\n]{10,80})', 'Stress'),
        ]

        for pattern, concept_type in concept_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                concept_name = match.group(1).strip()
                definition = match.group(2).strip()

                # Filtrage de qualité
                if (3 <= len(concept_name) <= 50 and
                        10 <= len(definition) <= 150 and
                        not any(char in definition for char in ['<', '>', '{', '}'])):  # Éviter HTML/code

                    # Nettoyage
                    concept_name = re.sub(r'\s+', ' ', concept_name)
                    definition = re.sub(r'\s+', ' ', definition)

                    # Recherche d'un article réglementaire dans le contexte
                    context = content[max(0, match.start() - 200):match.end() + 200]
                    article_match = re.search(r'[Aa]rticle\s+(\d+[a-z]?)', context)
                    regulatory_article = article_match.group(1) if article_match else None

                    # Création du concept
                    for scr_module in doc_source.scr_modules:
                        concept = SCRConcept(
                            concept_name=concept_name,
                            scr_module=scr_module,
                            definition=definition,
                            regulatory_article=regulatory_article,
                            source_document_id=doc_source.id
                        )

                        # Ajout à la base
                        concept_id = self.knowledge_base.add_scr_concept(concept)
                        if concept_id > 0:
                            concept.id = concept_id
                            extracted_concepts.append(concept)
                            self.logger.debug(f"Concept extrait: {concept_name}")

        return extracted_concepts

    def generate_optimized_prompt(self, config: PromptConfig) -> Dict[str, Any]:
        """
        Génération d'un prompt optimisé avec métadonnées complètes

        Args:
            config: Configuration de génération (IA, niveau, module, etc.)

        Returns:
            Dict contenant le prompt, métadonnées et recommandations d'utilisation
        """
        self.logger.info(
            f"Génération prompt: {config.ai_provider.value} - {config.scr_module.value} - {config.expertise_level.value}")

        start_time = datetime.now()

        try:
            # Génération du prompt via le PromptEngineer
            prompt_content = self.prompt_engineer.generate_prompt(config)

            # Collecte des métadonnées contextuelles
            relevant_docs = self.knowledge_base.get_documents_by_module(config.scr_module)
            concepts = self.knowledge_base.get_concepts_by_module(config.scr_module)

            generation_time = (datetime.now() - start_time).total_seconds()

            # Construction des métadonnées complètes
            metadata = {
                'config': {
                    'ai_provider': config.ai_provider.value,
                    'expertise_level': config.expertise_level.value,
                    'scr_module': config.scr_module.value,
                    'language': config.language,
                    'output_format': config.output_format,
                    'max_length': config.max_length,
                    'include_examples': config.include_examples,
                    'include_formulas': config.include_formulas
                },
                'generation_info': {
                    'timestamp': datetime.now().isoformat(),
                    'generation_time_seconds': generation_time,
                    'prompt_length_chars': len(prompt_content),
                    'prompt_length_words': len(prompt_content.split()),
                    'estimated_tokens': len(prompt_content.split()) * 1.3,  # Estimation tokens
                    'complexity_score': self._calculate_prompt_complexity(config, len(relevant_docs))
                },
                'knowledge_base_stats': {
                    'relevant_documents': len(relevant_docs),
                    'available_concepts': len(concepts),
                    'top_sources': [
                        {
                            'title': doc.title,
                            'type': doc.doc_type.value,
                            'reliability': doc.reliability_score,
                            'articles': doc.regulatory_articles[:3]
                        }
                        for doc in relevant_docs[:3]
                    ]
                },
                'quality_indicators': {
                    'has_regulatory_references': any(art.isdigit() for art in prompt_content.split()),
                    'has_formulas': 'SCR' in prompt_content and ('=' in prompt_content or '×' in prompt_content),
                    'has_examples': 'exemple' in prompt_content.lower() or 'example' in prompt_content.lower(),
                    'structure_score': self._assess_prompt_structure(prompt_content)
                }
            }

            # Génération des recommandations d'utilisation
            usage_recommendations = self._generate_usage_recommendations(config, metadata)

            # Calcul du score de qualité global
            quality_score = self._calculate_quality_score(prompt_content, metadata)

            self._prompts_generated += 1

            return {
                'prompt': prompt_content,
                'metadata': metadata,
                'usage_recommendations': usage_recommendations,
                'quality_score': quality_score,
                'success': True
            }

        except Exception as e:
            self.logger.error(f"Erreur génération prompt: {e}")
            return {
                'prompt': '',
                'metadata': {},
                'usage_recommendations': [],
                'quality_score': 0.0,
                'success': False,
                'error': str(e)
            }

    def _calculate_prompt_complexity(self, config: PromptConfig, docs_count: int) -> float:
        """Calcul du score de complexité du prompt (0-1)"""
        complexity = 0.0

        # Contribution du niveau d'expertise
        expertise_scores = {
            ExpertiseLevel.JUNIOR: 0.2,
            ExpertiseLevel.CONFIRMED: 0.5,
            ExpertiseLevel.EXPERT: 0.8,
            ExpertiseLevel.REGULATION_SPECIALIST: 1.0
        }
        complexity += expertise_scores.get(config.expertise_level, 0.5) * 0.4

        # Contribution de la longueur demandée
        complexity += min(config.max_length / 5000, 1.0) * 0.2

        # Contribution des options activées
        if config.include_formulas:
            complexity += 0.1
        if config.include_examples:
            complexity += 0.1

        # Contribution des données disponibles
        complexity += min(docs_count / 10, 1.0) * 0.2

        return min(complexity, 1.0)

    def _assess_prompt_structure(self, prompt_content: str) -> float:
        """Évaluation de la structure du prompt (0-1)"""
        structure_indicators = [
            'synthèse', 'introduction', 'méthodologie', 'formule', 'calcul',
            'exemple', 'règlement', 'article', 'référence', 'conclusion'
        ]

        content_lower = prompt_content.lower()
        found_indicators = sum(1 for indicator in structure_indicators if indicator in content_lower)

        return min(found_indicators / len(structure_indicators), 1.0)

    def _calculate_quality_score(self, prompt_content: str, metadata: Dict[str, Any]) -> float:
        """Calcul du score de qualité global (0-1)"""
        score = 0.0

        # Longueur appropriée
        length = len(prompt_content)
        if 1000 <= length <= 5000:
            score += 0.3
        elif length > 500:
            score += 0.1

        # Présence d'éléments clés
        quality_indicators = metadata.get('quality_indicators', {})
        if quality_indicators.get('has_regulatory_references'):
            score += 0.2
        if quality_indicators.get('has_formulas'):
            score += 0.2
        if quality_indicators.get('has_examples'):
            score += 0.1

        # Structure
        structure_score = quality_indicators.get('structure_score', 0)
        score += structure_score * 0.2

        return min(score, 1.0)

    def _generate_usage_recommendations(self, config: PromptConfig, metadata: Dict[str, Any]) -> List[str]:
        """Génération de recommandations d'utilisation contextuelles"""
        recommendations = []

        # Recommandations par IA
        ai_recommendations = {
            AIProvider.CLAUDE_SONNET_4: [
                "✅ Claude Sonnet 4 excelle pour ce type de prompt technique",
                "💡 Utilisez le contexte étendu pour inclure des documents sources",
                "⚡ Demandez des clarifications si les formules sont complexes"
            ],
            AIProvider.GPT_4: [
                "✅ GPT-4 excellent pour la structuration technique",
                "💡 Spécifiez le format de sortie désiré",
                "⚡ Validez les calculs numériques indépendamment"
            ],
            AIProvider.GEMINI_PRO: [
                "✅ Gemini Pro bon pour l'approche pédagogique",
                "💡 Exploitez sa créativité pour les exemples",
                "⚡ Vérifiez la précision des références réglementaires"
            ]
        }

        recommendations.extend(ai_recommendations.get(config.ai_provider, []))

        # Recommandations par niveau d'expertise
        if config.expertise_level == ExpertiseLevel.EXPERT:
            recommendations.append(
                "🎯 Niveau expert: vérifiez les références réglementaires avec les sources officielles")
        elif config.expertise_level == ExpertiseLevel.JUNIOR:
            recommendations.append("📚 Niveau junior: n'hésitez pas à demander des clarifications supplémentaires")

        # Recommandations par module SCR
        module_recommendations = {
            SCRModule.SPREAD: [
                "📊 Vérifiez les facteurs de stress avec les dernières révisions 2025",
                "🔢 Validez les exemples de calcul avec différentes notations"
            ],
            SCRModule.EQUITY: [
                "📈 Attention aux évolutions du dampener (±17% vs ±10%)",
                "🏢 Vérifiez les critères LTEI mis à jour"
            ],
            SCRModule.INTEREST_RATE: [
                "📉 Nouvelles corrélations spread/taux (25% vs 50%)",
                "⏰ Considérez les mesures transitoires en cours"
            ]
        }

        recommendations.extend(module_recommendations.get(config.scr_module, []))

        # Recommandations basées sur les données disponibles
        kb_stats = metadata.get('knowledge_base_stats', {})
        if kb_stats.get('relevant_documents', 0) == 0:
            recommendations.append("⚠️ Peu de sources disponibles: considérez ajouter des documents réglementaires")
        elif kb_stats.get('relevant_documents', 0) > 5:
            recommendations.append("📖 Nombreuses sources disponibles: prompt très contextualisé")

        # Recommandations de qualité
        quality_indicators = metadata.get('quality_indicators', {})
        if not quality_indicators.get('has_formulas'):
            recommendations.append("🧮 Demandez explicitement des formules si nécessaire")
        if not quality_indicators.get('has_examples'):
            recommendations.append("📝 Demandez des exemples chiffrés pour plus de clarté")

        return recommendations

    def batch_process_documents(self, documents_config: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Traitement en lot de plusieurs documents

        Args:
            documents_config: Liste des configurations de documents
                Format: [{'file_path': '...', 'doc_type': '...', 'scr_modules': [...], 'metadata': {...}}, ...]

        Returns:
            Dict avec résultats par fichier {file_path: success_boolean}
        """
        results = {}
        total = len(documents_config)

        self.logger.info(f"Début traitement en lot de {total} documents")

        for i, doc_config in enumerate(documents_config, 1):
            file_path = doc_config['file_path']

            self.logger.info(f"[{i}/{total}] Traitement: {Path(file_path).name}")

            try:
                success = self.add_document_source(
                    file_path_or_url=file_path,
                    doc_type=DocumentType(doc_config['doc_type']),
                    scr_modules=[SCRModule(m) for m in doc_config['scr_modules']],
                    **doc_config.get('metadata', {})
                )
                results[file_path] = success

                if success:
                    self.logger.info(f"✅ [{i}/{total}] Succès: {Path(file_path).name}")
                else:
                    self.logger.warning(f"⚠️ [{i}/{total}] Échec: {Path(file_path).name}")

            except Exception as e:
                self.logger.error(f"❌ [{i}/{total}] Erreur {Path(file_path).name}: {e}")
                results[file_path] = False

        success_count = sum(1 for r in results.values() if r)
        self.logger.info(f"Traitement en lot terminé: {success_count}/{total} réussis")

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Statistiques complètes du système

        Returns:
            Dict avec statistiques détaillées de la base de connaissances et du système
        """
        # Statistiques de la base de connaissances
        kb_stats = self.knowledge_base.get_statistics()

        # Statistiques système
        uptime = datetime.now() - self._startup_time

        system_stats = {
            'system_info': {
                'data_directory': str(self.data_dir),
                'documents_directory': str(self.documents_dir),
                'database_path': self.knowledge_base.db_path,
                'database_size_mb': Path(self.knowledge_base.db_path).stat().st_size / (1024 * 1024)
                if Path(self.knowledge_base.db_path).exists() else 0,
                'uptime_seconds': uptime.total_seconds(),
                'startup_time': self._startup_time.isoformat()
            },
            'session_stats': {
                'documents_processed': self._documents_processed,
                'prompts_generated': self._prompts_generated,
                'avg_processing_time': uptime.total_seconds() / max(self._documents_processed, 1)
            },
            'capabilities': {
                'supported_ai_providers': [p.value for p in AIProvider],
                'supported_scr_modules': [m.value for m in SCRModule],
                'supported_document_types': [t.value for t in DocumentType],
                'supported_languages': Config.SUPPORTED_LANGUAGES,
                'max_file_size_mb': Config.MAX_FILE_SIZE_MB
            },
            'version_info': {
                'system_version': '1.0.0',
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                'last_updated': datetime.now().isoformat()
            }
        }

        return {**kb_stats, **system_stats}

    def export_knowledge_base(self, export_path: str, format: str = 'json') -> bool:
        """
        Export de la base de connaissances

        Args:
            export_path: Chemin du fichier d'export
            format: Format d'export ('json', 'csv', 'yaml')

        Returns:
            True si l'export a réussi
        """
        try:
            self.logger.info(f"Début export base de connaissances vers {export_path}")

            # Récupération de toutes les données
            all_docs = []
            for module in SCRModule:
                docs = self.knowledge_base.get_documents_by_module(module)
                all_docs.extend([doc for doc in docs if doc not in all_docs])

            all_concepts = []
            for module in SCRModule:
                concepts = self.knowledge_base.get_concepts_by_module(module)
                all_concepts.extend(concepts)

            # Préparation des données d'export
            export_data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_documents': len(all_docs),
                    'total_concepts': len(all_concepts),
                    'system_version': '1.0.0'
                },
                'documents': [
                    {
                        'id': doc.id,
                        'title': doc.title,
                        'doc_type': doc.doc_type.value,
                        'scr_modules': [m.value for m in doc.scr_modules],
                        'regulatory_articles': doc.regulatory_articles,
                        'language': doc.language,
                        'reliability_score': doc.reliability_score,
                        'url': doc.url,
                        'publication_date': doc.publication_date.isoformat() if doc.publication_date else None
                    }
                    for doc in all_docs
                ],
                'concepts': [
                    {
                        'id': concept.id,
                        'concept_name': concept.concept_name,
                        'scr_module': concept.scr_module.value,
                        'definition': concept.definition,
                        'formula': concept.formula,
                        'regulatory_article': concept.regulatory_article,
                        'examples': concept.examples
                    }
                    for concept in all_concepts
                ]
            }

            # Export selon le format
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == 'json':
                import json
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            elif format.lower() == 'yaml':
                try:
                    import yaml
                    with open(export_path, 'w', encoding='utf-8') as f:
                        yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
                except ImportError:
                    self.logger.error("PyYAML non installé pour export YAML")
                    return False

            elif format.lower() == 'csv':
                import csv

                # Export des documents
                docs_path = export_path.with_suffix('.documents.csv')
                with open(docs_path, 'w', newline='', encoding='utf-8') as f:
                    if all_docs:
                        writer = csv.DictWriter(f, fieldnames=export_data['documents'][0].keys())
                        writer.writeheader()
                        writer.writerows(export_data['documents'])

                # Export des concepts
                concepts_path = export_path.with_suffix('.concepts.csv')
                with open(concepts_path, 'w', newline='', encoding='utf-8') as f:
                    if all_concepts:
                        writer = csv.DictWriter(f, fieldnames=export_data['concepts'][0].keys())
                        writer.writeheader()
                        writer.writerows(export_data['concepts'])

                self.logger.info(f"Export CSV: {docs_path} et {concepts_path}")

            else:
                raise ValueError(f"Format non supporté: {format}")

            self.logger.info(f"Export terminé: {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"Erreur lors de l'export: {e}")
            return False

    def search_documents(self,
                         query: str = None,
                         scr_modules: List[SCRModule] = None,
                         doc_types: List[DocumentType] = None,
                         min_reliability: float = 0.0) -> List[DocumentSource]:
        """
        Recherche avancée dans les documents

        Args:
            query: Requête textuelle (recherche dans titre et articles)
            scr_modules: Modules SCR à filtrer
            doc_types: Types de documents à filtrer
            min_reliability: Score de fiabilité minimum

        Returns:
            Liste des documents correspondants
        """
        all_docs = []

        # Collecte des documents par module si spécifié
        if scr_modules:
            for module in scr_modules:
                docs = self.knowledge_base.get_documents_by_module(module)
                all_docs.extend([doc for doc in docs if doc not in all_docs])
        else:
            # Tous les modules
            for module in SCRModule:
                docs = self.knowledge_base.get_documents_by_module(module)
                all_docs.extend([doc for doc in docs if doc not in all_docs])

        # Filtrage
        filtered_docs = []

        for doc in all_docs:
            # Filtre par type de document
            if doc_types and doc.doc_type not in doc_types:
                continue

            # Filtre par fiabilité
            if doc.reliability_score < min_reliability:
                continue

            # Filtre par requête textuelle
            if query:
                query_lower = query.lower()
                search_text = f"{doc.title} {' '.join(doc.regulatory_articles)}".lower()
                if query_lower not in search_text:
                    continue

            filtered_docs.append(doc)

        # Tri par pertinence (fiabilité puis titre)
        filtered_docs.sort(key=lambda doc: (-doc.reliability_score, doc.title))

        self.logger.info(f"Recherche: {len(filtered_docs)} documents trouvés")
        return filtered_docs

    def validate_system_health(self) -> Dict[str, Any]:
        """
        Validation de la santé du système

        Returns:
            Dict avec statut et diagnostics
        """
        health_report = {
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Vérification base de données
            try:
                stats = self.knowledge_base.get_statistics()
                health_report['checks']['database'] = 'ok'
                health_report['checks']['documents_count'] = stats['total_documents']
            except Exception as e:
                health_report['checks']['database'] = 'error'
                health_report['errors'].append(f"Erreur base de données: {e}")
                health_report['overall_status'] = 'unhealthy'

            # Vérification répertoires
            if not self.data_dir.exists():
                health_report['errors'].append(f"Répertoire de données manquant: {self.data_dir}")
                health_report['overall_status'] = 'unhealthy'
            else:
                health_report['checks']['data_directory'] = 'ok'

            # Vérification espace disque
            try:
                import shutil
                total, used, free = shutil.disk_usage(self.data_dir)
                free_gb = free / (1024 ** 3)
                if free_gb < 1.0:  # Moins de 1GB libre
                    health_report['warnings'].append(f"Espace disque faible: {free_gb:.1f}GB")
                health_report['checks']['disk_space_gb'] = free_gb
            except:
                health_report['warnings'].append("Impossible de vérifier l'espace disque")

            # Vérification des composants
            try:
                # Test génération prompt simple
                test_config = PromptConfig(
                    ai_provider=AIProvider.CLAUDE_SONNET_4,
                    expertise_level=ExpertiseLevel.EXPERT,
                    scr_module=SCRModule.SPREAD,
                    max_length=100
                )

                result = self.prompt_engineer.generate_prompt(test_config)
                if len(result) > 50:
                    health_report['checks']['prompt_generation'] = 'ok'
                else:
                    health_report['warnings'].append("Génération de prompts limitée")
            except Exception as e:
                health_report['checks']['prompt_generation'] = 'error'
                health_report['errors'].append(f"Erreur génération prompt: {e}")

            # Statut final
            if health_report['errors']:
                health_report['overall_status'] = 'unhealthy'
            elif health_report['warnings']:
                health_report['overall_status'] = 'warning'

        except Exception as e:
            health_report['overall_status'] = 'critical'
            health_report['errors'].append(f"Erreur critique validation: {e}")

        return health_report

    def cleanup_old_data(self, days_threshold: int = 30) -> Dict[str, int]:
        """
        Nettoyage des données anciennes

        Args:
            days_threshold: Seuil en jours pour considérer les données comme anciennes

        Returns:
            Dict avec statistiques de nettoyage
        """
        from datetime import timedelta

        cleanup_stats = {
            'documents_removed': 0,
            'concepts_removed': 0,
            'files_removed': 0
        }

        try:
            threshold_date = datetime.now() - timedelta(days=days_threshold)

            # Note: Cette fonctionnalité nécessiterait des modifications
            # de la base de données pour inclure des timestamps de dernière utilisation

            self.logger.info(f"Nettoyage des données antérieures au {threshold_date.date()}")

            # Pour l'instant, juste un placeholder
            # Dans une implémentation complète, on supprimerait :
            # - Documents non utilisés depuis X jours
            # - Concepts orphelins
            # - Fichiers temporaires

            self.logger.info("Nettoyage terminé")

        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage: {e}")

        return cleanup_stats

    def close(self):
        """Fermeture propre du système"""
        try:
            # Statistiques finales
            uptime = datetime.now() - self._startup_time
            self.logger.info(f"Fermeture du système après {uptime}")
            self.logger.info(f"Documents traités: {self._documents_processed}")
            self.logger.info(f"Prompts générés: {self._prompts_generated}")

            # Fermeture de la base de données
            self.knowledge_base.close()

            self.logger.info("SCR Prompt Generator fermé proprement")

        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture: {e}")

    def __enter__(self):
        """Support du context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique avec context manager"""
        self.close()

        # Gestion des exceptions
        if exc_type:
            self.logger.error(f"Exception dans le context manager: {exc_type.__name__}: {exc_val}")

        return False  # Ne pas supprimer l'exception


# ==========================================
# FONCTIONS UTILITAIRES GLOBALES
# ==========================================

def create_default_generator() -> SCRPromptGenerator:
    """
    Création d'un générateur avec configuration par défaut

    Returns:
        Instance configurée du SCRPromptGenerator
    """
    return SCRPromptGenerator()


def quick_generate_prompt(scr_module: str,
                          ai_provider: str = "claude-sonnet-4",
                          expertise_level: str = "expert") -> str:
    """
    Génération rapide d'un prompt sans configuration avancée

    Args:
        scr_module: Module SCR (ex: "spread", "equity")
        ai_provider: IA à utiliser (défaut: "claude-sonnet-4")
        expertise_level: Niveau d'expertise (défaut: "expert")

    Returns:
        Contenu du prompt généré
    """
    with create_default_generator() as generator:
        config = PromptConfig(
            ai_provider=AIProvider(ai_provider.replace('-', '_').upper()),
            expertise_level=ExpertiseLevel(expertise_level.upper()),
            scr_module=SCRModule(scr_module.upper())
        )

        result = generator.generate_optimized_prompt(config)
        return result.get('prompt', '')


def batch_add_documents(documents_list: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Ajout en lot de documents avec configuration simplifiée

    Args:
        documents_list: Liste de dictionnaires avec clés 'file_path', 'doc_type', 'scr_modules'

    Returns:
        Dict avec résultats par fichier
    """
    with create_default_generator() as generator:
        return generator.batch_process_documents(documents_list)


# ==========================================
# POINT D'ENTRÉE POUR TESTS
# ==========================================

if __name__ == "__main__":
    # Test basique si le fichier est exécuté directement
    print("🧪 Test basique du module main.py")

    try:
        # Test d'initialisation
        generator = SCRPromptGenerator()
        print("✅ Générateur initialisé")

        # Test des statistiques
        stats = generator.get_statistics()
        print(f"✅ Statistiques: {stats['total_documents']} documents")

        # Test de validation
        health = generator.validate_system_health()
        print(f"✅ Santé système: {health['overall_status']}")

        # Test génération prompt simple
        config = PromptConfig(
            ai_provider=AIProvider.CLAUDE_SONNET_4,
            expertise_level=ExpertiseLevel.EXPERT,
            scr_module=SCRModule.SPREAD
        )

        result = generator.generate_optimized_prompt(config)
        if result['success']:
            print(f"✅ Prompt généré: {len(result['prompt'])} caractères")
        else:
            print("⚠️ Échec génération prompt")

        generator.close()
        print("🎉 Test basique réussi!")

    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback

        traceback.print_exc()