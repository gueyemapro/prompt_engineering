# ==========================================
# Fichier: src/prompts/generator.py
# ==========================================

import logging
from typing import Dict, List, Any
from ..knowledge.database import SCRKnowledgeBase
from ..knowledge.models import DocumentSource, PromptConfig
from ..config import AIProvider, ExpertiseLevel, SCRModule
from .templates import PromptTemplateLibrary


class PromptEngineer:
    """Moteur principal de génération de prompts optimisés"""

    def __init__(self, knowledge_base: SCRKnowledgeBase):
        self.kb = knowledge_base
        self.template_library = PromptTemplateLibrary()
        self.logger = logging.getLogger(__name__)

    def generate_prompt(self, config: PromptConfig) -> str:
        """
        Génération du prompt optimisé selon la configuration

        Args:
            config: Configuration de génération

        Returns:
            Prompt optimisé
        """
        self.logger.info(f"Génération prompt: {config.ai_provider.value} - {config.scr_module.value}")

        # 1. Sélection du template approprié
        template = self.template_library.get_template(config.ai_provider, config.expertise_level)

        # 2. Collecte des données contextuelles
        context_data = self._gather_context_data(config)

        # 3. Rendu du template
        try:
            rendered_prompt = template.render(**context_data)
            self.logger.info(f"Prompt généré avec succès ({len(rendered_prompt)} caractères)")
            return rendered_prompt

        except Exception as e:
            self.logger.error(f"Erreur génération prompt: {e}")
            raise

    def _gather_context_data(self, config: PromptConfig) -> Dict[str, Any]:
        """Collecte des données contextuelles pour le prompt"""

        # Sources réglementaires pertinentes
        relevant_docs = self.kb.get_documents_by_module(config.scr_module, limit=5)
        regulatory_sources = self._format_regulatory_sources(relevant_docs)

        # Concepts clés du module
        key_concepts = self._extract_key_concepts(config.scr_module)

        # Exigences de structure
        structure_requirements = self._generate_structure_requirements(config)

        # Exemples concrets
        concrete_examples = self._generate_examples(config.scr_module)

        # Exigences qualité
        quality_requirements = self._define_quality_requirements(config)

        return {
            'experience_years': '15',
            'specialization': f'modélisation des risques de {config.scr_module.value}',
            'scr_module_name': self._get_module_french_name(config.scr_module),
            'regulatory_sources': regulatory_sources,
            'key_concepts': key_concepts,
            'structure_requirements': structure_requirements,
            'concrete_examples': concrete_examples,
            'quality_requirements': quality_requirements,
            'word_count': str(config.max_length)
        }

    def _format_regulatory_sources(self, docs: List[DocumentSource]) -> str:
        """Formatage des sources réglementaires"""
        if not docs:
            return "### Sources à rechercher :\n- Règlement délégué (UE) 2015/35\n- Guidelines EIOPA pertinentes"

        sources = ["### Sources prioritaires identifiées :"]
        for i, doc in enumerate(docs[:5], 1):
            source_text = f"{i}. **{doc.title}**"
            if doc.regulatory_articles:
                articles = ', '.join(doc.regulatory_articles[:3])
                source_text += f" (Articles: {articles})"
            if doc.url:
                source_text += f"\n   - URL: {doc.url}"
            if doc.reliability_score:
                source_text += f" (Fiabilité: {doc.reliability_score:.1f}/1.0)"
            sources.append(source_text)

        return "\n".join(sources)

    def _extract_key_concepts(self, scr_module: SCRModule) -> str:
        """Extraction des concepts clés par module SCR"""

        # Récupération des concepts depuis la base
        concepts_from_db = self.kb.get_concepts_by_module(scr_module)

        # Concepts par défaut si base vide
        default_concepts = {
            SCRModule.SPREAD: [
                "Facteurs de stress par notation de crédit (AAA à Non noté)",
                "Duration modifiée et calcul de sensibilité aux spreads",
                "Traitement des obligations non notées (choc 30bp × duration)",
                "Corrélations avec autres modules (taux, actions)",
                "Exemptions souveraines et règles d'application",
                "Formule SCR_spread = SCR_bonds + SCR_securitisation + SCR_cd",
                "Grille des facteurs par notation et duration",
                "Règles de plafonnement (100% de la valeur)"
            ],
            SCRModule.INTEREST_RATE: [
                "Chocs de taux haussier et baissier",
                "Courbe des taux sans risque et extrapolation",
                "Duration et convexité des passifs",
                "Effet d'absorption par les provisions techniques",
                "Corrélations avec module spread (50% → 25%)",
                "Treatment des instruments dérivés de taux"
            ],
            SCRModule.EQUITY: [
                "Classification Type I (39%) et Type II (49%)",
                "Ajustement symétrique (dampener ±17%)",
                "Actions de long terme (LTEI) - traitement favorisé",
                "Participations dans institutions financières",
                "Duration-based equity sub-module",
                "Critères d'éligibilité et conditions"
            ],
            SCRModule.CONCENTRATION: [
                "Seuils de concentration par émetteur",
                "Facteurs de granularité",
                "Traitement des expositions souveraines",
                "Calcul des excès de concentration",
                "Diversification géographique et sectorielle"
            ],
            SCRModule.CURRENCY: [
                "Chocs de change par devise (25% standard)",
                "Corrélations entre devises",
                "Matching currency des actifs/passifs",
                "Exemptions pour devises locales",
                "Traitement des dérivés de change"
            ]
        }

        # Combinaison concepts DB + défaut
        concepts = []

        # Ajout des concepts de la base
        for concept in concepts_from_db:
            concepts.append(f"**{concept.concept_name}** : {concept.definition}")

        # Ajout des concepts par défaut si pas assez
        if len(concepts) < 5:
            default_list = default_concepts.get(scr_module, ["Concepts à définir"])
            for concept in default_list[:8 - len(concepts)]:
                concepts.append(f"- {concept}")

        return "\n".join(concepts)

    def _generate_structure_requirements(self, config: PromptConfig) -> str:
        """Génération des exigences de structure selon le niveau"""

        base_structure = {
            ExpertiseLevel.EXPERT: """
### 1. SYNTHÈSE EXÉCUTIVE (150 mots max)
- Objectif réglementaire et périmètre d'application
- Impact typique sur le ratio de solvabilité
- Points d'attention critiques

### 2. CADRE RÉGLEMENTAIRE DE RÉFÉRENCE  
- Articles du Règlement délégué (numéros précis)
- Directive mère et références pertinentes
- Guidelines EIOPA et standards techniques
- Évolutions récentes et futures

### 3. MÉTHODOLOGIE DE CALCUL DÉTAILLÉE
- Formule principale avec notation rigoureuse
- Paramètres et variables (définitions précises)
- Algorithme de calcul étape par étape
- Cas particuliers et exceptions

### 4. ASPECTS OPÉRATIONNELS
- Données requises et sources
- Fréquence de calcul et mise à jour
- Contrôles de cohérence et validation
- Interface avec autres modules SCR

### 5. EXEMPLES CHIFFRÉS CONCRETS
- Au moins 2 exemples détaillés
- Calculs pas à pas avec résultats
- Cas réalistes d'assureur français

### 6. INTERACTIONS ET CORRÉLATIONS
- Matrice de corrélation avec autres risques
- Effet de diversification
- Absorption par le passif

### 7. ÉVOLUTIONS RÉGLEMENTAIRES
- Révisions 2019 et 2025-2026
- Impact estimé des changements
- Calendrier d'application
            """,

            ExpertiseLevel.CONFIRMED: """
### 1. Introduction et Objectifs
- Contexte réglementaire du module
- Objectif de couverture du risque

### 2. Formule de Calcul
- Formule principale
- Définition des variables
- Paramètres clés

### 3. Données et Paramètres
- Inputs nécessaires
- Sources de données
- Fréquence de mise à jour

### 4. Exemples Pratiques
- Cas d'application concrets
- Calculs détaillés

### 5. Points d'Attention
- Difficultés d'implémentation
- Contrôles à effectuer
- Interactions avec autres modules
            """,

            ExpertiseLevel.JUNIOR: """
### 1. Présentation Générale
- Qu'est-ce que ce module SCR ?
- Pourquoi est-il important ?

### 2. Méthode de Calcul Simplifiée
- Formule de base
- Étapes principales

### 3. Exemple Simple
- Cas concret avec chiffres
- Calcul étape par étape

### 4. Points Clés à Retenir
- Éléments essentiels
- Erreurs à éviter
            """
        }

        return base_structure.get(config.expertise_level, base_structure[ExpertiseLevel.CONFIRMED])

    def _generate_examples(self, scr_module: SCRModule) -> str:
        """Génération d'exemples concrets par module"""

        examples_map = {
            SCRModule.SPREAD: """
#### Exemple 1 : Obligation Corporate BBB
- **Exposition** : 100M€ d'obligations Renault 2030
- **Characteristics** : Notation BBB, duration modifiée 6,5 ans
- **Calcul** : Stress = 6,5 × 2,5% = 16,25%
- **SCR** : 100M€ × 16,25% = 16,25M€
- **Impact net** : après corrélations et absorption passif

#### Exemple 2 : Portefeuille diversifié  
- **Composition** : 60% AAA (200M€), 30% BBB (100M€), 10% non noté (33M€)
- **Calcul par tranche** avec facteurs respectifs
- **Agrégation** : effet de diversification limité
- **SCR total** : formule quadratique avec corrélations
            """,

            SCRModule.EQUITY: """
#### Exemple 1 : Actions européennes Type I
- **Portefeuille** : 500M€ d'actions CAC 40
- **Choc de base** : 39% (avant ajustements)
- **Ajustement symétrique** : +5% (market conditions)
- **Choc final** : 39% + 5% = 44%
- **SCR** : 500M€ × 44% = 220M€
            """,

            SCRModule.INTEREST_RATE: """
#### Exemple 1 : Portefeuille obligations souveraines
- **Duration moyenne** : 8,2 ans
- **Choc haussier** : selon courbe réglementaire
- **Choc baissier** : plancher à 0% (si applicable)
- **Impact sur provisions** : calcul différentiel
- **SCR final** : max(choc hausse, choc baisse)
            """
        }

        return examples_map.get(scr_module, """
#### À définir selon le module spécifique
- Exemple concret avec données réalistes
- Calcul détaillé étape par étape
- Résultats commentés et contextualisés
        """)

    def _define_quality_requirements(self, config: PromptConfig) -> str:
        """Définition des exigences qualité selon l'IA et le niveau"""

        base_requirements = """
### Format et Style
- **Langue** : français professionnel, niveau expert
- **Formules** : notation mathématique claire (LaTeX si complexe)
- **Références** : numéros d'articles précis, pas de paraphrase
- **Structure** : titres courts, paragraphes denses

### Précision Technique
- **Chiffres exacts** : facteurs officiels, pas d'approximation
- **Cohérence** : liens entre sections, renvois internes
- **Sources** : citations directes des textes réglementaires
- **Exemples** : calculs vérifiables et représentatifs
        """

        ai_specific = {
            AIProvider.CLAUDE_SONNET_4: """
### Spécificités Claude
- **Raisonnement** : étapes logiques détaillées, analyse structurée
- **Contexte** : utilisation optimale du contexte étendu
- **Nuances** : gestion des cas particuliers et exceptions
- **Synthèse** : capacité à condenser l'information essentielle
            """,

            AIProvider.GPT_4: """
### Spécificités GPT-4
- **Précision** : formulations exactes et non ambiguës
- **Structure** : organisation claire avec numérotation
- **Exemples** : applications pratiques détaillées
- **Références** : citations exactes et vérifiables
            """,

            AIProvider.GEMINI_PRO: """
### Spécificités Gemini
- **Créativité** : approches pédagogiques variées
- **Multiformat** : tableaux, listes, diagrammes textuels
- **Comparaisons** : mises en perspective avec autres modules
- **Synthèse** : résumés exécutifs percutants
            """
        }

        specific_req = ai_specific.get(config.ai_provider, "")

        return base_requirements + specific_req

    def _get_module_french_name(self, scr_module: SCRModule) -> str:
        """Traduction des noms de modules en français"""
        names_map = {
            SCRModule.SPREAD: "SCR de spread (risque de crédit)",
            SCRModule.INTEREST_RATE: "SCR de taux d'intérêt",
            SCRModule.EQUITY: "SCR actions",
            SCRModule.CURRENCY: "SCR de change",
            SCRModule.CONCENTRATION: "SCR de concentration",
            SCRModule.MARKET_GLOBAL: "SCR de marché global",
            SCRModule.COUNTERPARTY: "SCR de contrepartie",
            SCRModule.OPERATIONAL: "SCR opérationnel",
            SCRModule.LIFE: "SCR vie",
            SCRModule.NON_LIFE: "SCR non-vie"
        }
        return names_map.get(scr_module, f"SCR {scr_module.value}")