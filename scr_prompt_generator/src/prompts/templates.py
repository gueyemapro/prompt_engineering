# ==========================================
# ÉTAPE 5 : GÉNÉRATEUR DE PROMPTS
# Fichier: src/prompts/templates.py
# ==========================================

from typing import Dict, List
from ..config import AIProvider, ExpertiseLevel, SCRModule


class PromptTemplate:
    """Template de prompt avec variables dynamiques"""

    def __init__(self, name: str, content: str, variables: List[str]):
        self.name = name
        self.content = content
        self.variables = variables

    def render(self, **kwargs) -> str:
        """Rendu du template avec substitution des variables"""
        rendered = self.content
        for var in self.variables:
            if var in kwargs:
                rendered = rendered.replace(f"{{{var}}}", str(kwargs[var]))
        return rendered

    def get_missing_variables(self, **kwargs) -> List[str]:
        """Retourne les variables manquantes"""
        return [var for var in self.variables if var not in kwargs]


class PromptTemplateLibrary:
    """Bibliothèque de templates de prompts"""

    def __init__(self):
        self.templates = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Chargement des templates par défaut"""

        # Template Claude Sonnet 4 - Expert
        claude_expert = PromptTemplate(
            name="claude_sonnet_4_expert",
            content="""# CONTEXTE & EXPERTISE
Tu es un actuaire expert en Solvabilité 2 avec {experience_years}+ années d'expérience dans le calcul des SCR. 
Ta spécialité : {specialization}. Tu maîtrises parfaitement le Règlement délégué (UE) 2015/35 et ses évolutions récentes.

# MISSION
Créer une fiche technique professionnelle ultra-complète sur le **calcul du {scr_module_name}** sous Solvabilité 2, 
destinée à des actuaires confirmés pour usage interne en compagnie d'assurance.

# SOURCES RÉGLEMENTAIRES PRIORITAIRES
{regulatory_sources}

# CONCEPTS CLÉS À COUVRIR
{key_concepts}

# STRUCTURE OBLIGATOIRE
{structure_requirements}

# EXEMPLES CONCRETS REQUIS
{concrete_examples}

# EXIGENCES DE QUALITÉ CRITIQUE
{quality_requirements}

**RENDU ATTENDU :** Document de {word_count} mots, niveau référence technique interne, 
directement utilisable pour implémentation et audit réglementaire.""",
            variables=["experience_years", "specialization", "scr_module_name",
                       "regulatory_sources", "key_concepts", "structure_requirements",
                       "concrete_examples", "quality_requirements", "word_count"]
        )

        # Template Claude Sonnet 4 - Confirmé
        claude_confirmed = PromptTemplate(
            name="claude_sonnet_4_confirmed",
            content="""# EXPERT SOLVABILITÉ 2
Tu es un actuaire spécialisé en Solvabilité 2 avec une expertise approfondie en {scr_module_name}.

# OBJECTIF
Rédiger un guide technique détaillé sur le **{scr_module_name}** pour des actuaires confirmés.

# SOURCES À UTILISER
{regulatory_sources}

# POINTS CLÉS À TRAITER
{key_concepts}

# STRUCTURE DEMANDÉE
{structure_requirements}

# EXEMPLES PRATIQUES
{concrete_examples}

# CRITÈRES DE QUALITÉ
- Formules mathématiques précises
- Références réglementaires exactes
- Exemples chiffrés réalistes
- Niveau technique approprié

**Livrable :** Guide de {word_count} mots maximum, prêt pour utilisation opérationnelle.""",
            variables=["scr_module_name", "regulatory_sources", "key_concepts",
                       "structure_requirements", "concrete_examples", "word_count"]
        )

        # Template GPT-4 - Expert
        gpt4_expert = PromptTemplate(
            name="gpt4_expert",
            content="""You are a Solvency II actuary with deep expertise in {scr_module_name} risk calculations.

OBJECTIVE: Create a comprehensive technical guide for {scr_module_name} SCR calculation.

TARGET AUDIENCE: Expert actuaries in insurance companies.

REGULATORY FRAMEWORK:
{regulatory_sources}

KEY REQUIREMENTS:
1. Mathematical formulas with precise notation
2. Regulatory article references  
3. Practical examples with calculations
4. Implementation guidance

STRUCTURE:
{structure_requirements}

EXAMPLES:
{concrete_examples}

QUALITY STANDARDS:
{quality_requirements}

OUTPUT: {word_count} words technical document, ready for professional use.""",
            variables=["scr_module_name", "regulatory_sources", "structure_requirements",
                       "concrete_examples", "quality_requirements", "word_count"]
        )

        # Template Gemini Pro - Confirmé
        gemini_confirmed = PromptTemplate(
            name="gemini_pro_confirmed",
            content="""# Assistant Expert en Réglementation Solvabilité 2

**Spécialisation :** {scr_module_name}

## Mission
Créer un document technique sur le calcul du {scr_module_name} sous Solvabilité 2.

## Public cible
Actuaires confirmés en assurance

## Sources réglementaires
{regulatory_sources}

## Concepts essentiels
{key_concepts}

## Plan à suivre
{structure_requirements}

## Exemples attendus
{concrete_examples}

## Format final
Document technique de {word_count} mots avec formules, exemples et références.""",
            variables=["scr_module_name", "regulatory_sources", "key_concepts",
                       "structure_requirements", "concrete_examples", "word_count"]
        )

        # Ajout des templates
        self.templates["claude_sonnet_4_expert"] = claude_expert
        self.templates["claude_sonnet_4_confirmed"] = claude_confirmed
        self.templates["gpt4_expert"] = gpt4_expert
        self.templates["gemini_pro_confirmed"] = gemini_confirmed

    def get_template(self, ai_provider: AIProvider, expertise_level: ExpertiseLevel) -> PromptTemplate:
        """Récupération du template approprié"""
        template_key = f"{ai_provider.value}_{expertise_level.value}"

        if template_key in self.templates:
            return self.templates[template_key]

        # Fallback vers template générique
        fallbacks = [
            f"{ai_provider.value}_expert",
            f"{ai_provider.value}_confirmed",
            "claude_sonnet_4_expert"
        ]

        for fallback in fallbacks:
            if fallback in self.templates:
                return self.templates[fallback]

        # Si aucun template trouvé, retourner le premier
        return list(self.templates.values())[0]

    def add_template(self, template: PromptTemplate):
        """Ajout d'un template personnalisé"""
        self.templates[template.name] = template

    def list_templates(self) -> List[str]:
        """Liste des templates disponibles"""
        return list(self.templates.keys())