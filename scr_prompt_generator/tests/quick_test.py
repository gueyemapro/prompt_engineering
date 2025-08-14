# ==========================================
# 1. TEST RAPIDE - VÉRIFICATION DE BASE
# Fichier: quick_test.py
# ==========================================

def quick_test():
    """Test rapide pour vérifier que tout fonctionne"""
    print("🚀 TEST RAPIDE - VÉRIFICATION DE BASE")
    print("=" * 50)

    try:
        # Test des imports
        print("1. Test des imports...")
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig
        from src.config import AIProvider, ExpertiseLevel, SCRModule
        print("✅ Imports réussis")

        # Test initialisation
        print("\n2. Test initialisation...")
        generator = SCRPromptGenerator()
        print("✅ Générateur initialisé")

        # Test génération simple
        print("\n3. Test génération de prompt...")
        config = PromptConfig(
            ai_provider=AIProvider.CLAUDE_SONNET_4,
            expertise_level=ExpertiseLevel.EXPERT,
            scr_module=SCRModule.SPREAD
        )

        result = generator.generate_optimized_prompt(config)
        print(f"✅ Prompt généré: {len(result['prompt'])} caractères")

        # Test statistiques
        print("\n4. Test statistiques...")
        stats = generator.get_statistics()
        print(f"✅ Stats récupérées: {stats['total_documents']} documents")

        generator.close()
        print("\n🎉 TOUS LES TESTS DE BASE PASSÉS!")
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False