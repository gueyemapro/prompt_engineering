# ==========================================
# SCRIPT DE TEST POUR L'ÉTAPE 5
# Fichier: test_prompt_generator.py (à la racine)
# ==========================================

def test_prompt_generator():
    """Test du générateur de prompts"""
    import tempfile
    import os
    from src.knowledge.database import SCRKnowledgeBase
    from src.knowledge.models import PromptConfig, DocumentSource, SCRConcept
    from src.prompts.generator import PromptEngineer
    from src.config import AIProvider, ExpertiseLevel, SCRModule, DocumentType
    from datetime import date

    print("🧪 TEST DU GÉNÉRATEUR DE PROMPTS")
    print("=" * 45)

    # Création d'une base de test temporaire
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        test_db_path = tmp_db.name

    try:
        # Initialisation avec données de test
        with SCRKnowledgeBase(test_db_path) as kb:

            # Ajout d'un document de test
            doc = DocumentSource(
                id="reglement_2015_35",
                title="Règlement délégué (UE) 2015/35",
                doc_type=DocumentType.REGULATION_EU,
                url="https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A32015R0035",
                publication_date=date(2015, 1, 17),
                regulatory_articles=["175", "176", "180", "181"],
                scr_modules=[SCRModule.SPREAD, SCRModule.CONCENTRATION],
                reliability_score=1.0,
                content_hash="test123"
            )
            kb.add_document(doc)

            # Ajout d'un concept de test
            concept = SCRConcept(
                concept_name="Facteur de stress spread",
                scr_module=SCRModule.SPREAD,
                definition="Facteur multiplicateur appliqué à la duration selon la notation de crédit",
                formula="Stress_i = Duration_i × Facteur_notation_i",
                regulatory_article="180",
                examples=["BBB 5 ans: 2.5%", "AAA 10 ans: 0.9%"]
            )
            kb.add_scr_concept(concept)

            # Initialisation du générateur
            prompt_engineer = PromptEngineer(kb)

            # Test 1: Claude Expert
            print("\n1. Test Claude Sonnet 4 - Expert")
            config = PromptConfig(
                ai_provider=AIProvider.CLAUDE_SONNET_4,
                expertise_level=ExpertiseLevel.EXPERT,
                scr_module=SCRModule.SPREAD,
                max_length=3000
            )

            prompt = prompt_engineer.generate_prompt(config)
            print(f"✅ Prompt généré: {len(prompt)} caractères")
            print(f"✅ Contient 'SCR de spread': {'SCR de spread' in prompt}")
            print(f"✅ Contient référence réglementaire: {'180' in prompt}")

            # Test 2: GPT-4 Confirmé
            print("\n2. Test GPT-4 - Confirmé")
            config2 = PromptConfig(
                ai_provider=AIProvider.GPT_4,
                expertise_level=ExpertiseLevel.CONFIRMED,
                scr_module=SCRModule.EQUITY,
                max_length=2000
            )

            prompt2 = prompt_engineer.generate_prompt(config2)
            print(f"✅ Prompt généré: {len(prompt2)} caractères")
            print(f"✅ Contient 'equity': {'equity' in prompt2.lower()}")

            # Test 3: Gemini Junior
            print("\n3. Test Gemini Pro - Junior")
            config3 = PromptConfig(
                ai_provider=AIProvider.GEMINI_PRO,
                expertise_level=ExpertiseLevel.JUNIOR,
                scr_module=SCRModule.INTEREST_RATE
            )

            prompt3 = prompt_engineer.generate_prompt(config3)
            print(f"✅ Prompt généré: {len(prompt3)} caractères")

            # Affichage d'un exemple de prompt (tronqué)
            print(f"\n📄 EXEMPLE DE PROMPT (Claude Expert - 500 premiers caractères):")
            print("-" * 60)
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            print("-" * 60)

            print(f"\n🎉 TOUS LES TESTS PROMPT GENERATOR PASSÉS!")

    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

    finally:
        # Nettoyage
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    return True


if __name__ == "__main__":
    test_prompt_generator()