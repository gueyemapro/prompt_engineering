# ==========================================
# 3. TEST COMPARATIF MULTI-IA
# Fichier: test_multi_ai.py
# ==========================================

def test_multi_ai_comparison():
    """Test comparatif entre différentes IA"""
    print("🤖 TEST COMPARATIF MULTI-IA")
    print("=" * 35)

    try:
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig
        from src.config import AIProvider, ExpertiseLevel, SCRModule

        generator = SCRPromptGenerator()

        # Configurations à tester
        test_configs = [
            (AIProvider.CLAUDE_SONNET_4, ExpertiseLevel.EXPERT, "Claude Sonnet 4 Expert"),
            (AIProvider.GPT_4, ExpertiseLevel.EXPERT, "GPT-4 Expert"),
            (AIProvider.CLAUDE_SONNET_4, ExpertiseLevel.CONFIRMED, "Claude Sonnet 4 Confirmé"),
            (AIProvider.GEMINI_PRO, ExpertiseLevel.CONFIRMED, "Gemini Pro Confirmé"),
        ]

        results = {}

        for ai_provider, expertise_level, description in test_configs:
            print(f"\n🧪 Test: {description}")

            config = PromptConfig(
                ai_provider=ai_provider,
                expertise_level=expertise_level,
                scr_module=SCRModule.SPREAD,
                max_length=2500
            )

            import time
            start_time = time.time()

            result = generator.generate_optimized_prompt(config)

            generation_time = time.time() - start_time

            if result['success']:
                results[description] = {
                    'prompt': result['prompt'],
                    'length': len(result['prompt']),
                    'words': len(result['prompt'].split()),
                    'generation_time': generation_time,
                    'metadata': result['metadata'],
                    'recommendations': result['usage_recommendations']
                }

                print(f"   ✅ Généré: {len(result['prompt'])} caractères")
                print(f"   ⏱️ Temps: {generation_time:.3f}s")
                print(f"   💡 Recommandations: {len(result['usage_recommendations'])}")
            else:
                print(f"   ❌ Échec de génération")

        # Comparaison des résultats
        print(f"\n📊 COMPARAISON DES RÉSULTATS:")
        print("-" * 60)
        print(f"{'Configuration':<25} {'Longueur':<10} {'Mots':<8} {'Temps(s)':<10}")
        print("-" * 60)

        for desc, data in results.items():
            print(f"{desc:<25} {data['length']:<10} {data['words']:<8} {data['generation_time']:<10.3f}")

        # Analyse des différences
        print(f"\n🔍 ANALYSE DES DIFFÉRENCES:")

        if results:
            # Prompt le plus long
            longest = max(results.items(), key=lambda x: x[1]['length'])
            print(f"   📏 Plus long: {longest[0]} ({longest[1]['length']} caractères)")

            # Prompt le plus rapide
            fastest = min(results.items(), key=lambda x: x[1]['generation_time'])
            print(f"   ⚡ Plus rapide: {fastest[0]} ({fastest[1]['generation_time']:.3f}s)")

            # Prompt avec le plus de recommandations
            most_recs = max(results.items(), key=lambda x: len(x[1]['recommendations']))
            print(f"   💡 Plus de conseils: {most_recs[0]} ({len(most_recs[1]['recommendations'])} recommandations)")

        # Affichage d'un exemple de différence
        if len(results) >= 2:
            configs = list(results.keys())
            config1, config2 = configs[0], configs[1]

            print(f"\n📄 COMPARAISON D'EXTRAITS:")
            print(f"\n{config1} (200 premiers caractères):")
            print(f"'{results[config1]['prompt'][:200]}...'")

            print(f"\n{config2} (200 premiers caractères):")
            print(f"'{results[config2]['prompt'][:200]}...'")

        generator.close()
        print(f"\n🎉 TEST COMPARATIF TERMINÉ!")
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False