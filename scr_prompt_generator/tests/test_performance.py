# ==========================================
# 4. TEST DE PERFORMANCE
# Fichier: test_performance.py
# ==========================================

def test_performance():
    """Test de performance et de charge"""
    print("⚡ TEST DE PERFORMANCE")
    print("=" * 30)

    try:
        import time
        import statistics
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig
        from src.config import AIProvider, ExpertiseLevel, SCRModule

        generator = SCRPromptGenerator()

        # Configuration de test
        config = PromptConfig(
            ai_provider=AIProvider.CLAUDE_SONNET_4,
            expertise_level=ExpertiseLevel.EXPERT,
            scr_module=SCRModule.SPREAD,
            max_length=3000
        )

        # Test de génération multiple
        print("🔄 Test génération multiple...")
        times = []
        prompt_lengths = []

        for i in range(5):
            print(f"   Génération {i + 1}/5...")

            start_time = time.time()
            result = generator.generate_optimized_prompt(config)
            end_time = time.time()

            generation_time = end_time - start_time
            times.append(generation_time)

            if result['success']:
                prompt_lengths.append(len(result['prompt']))
                print(f"   ✅ {generation_time:.3f}s - {len(result['prompt'])} caractères")
            else:
                print(f"   ❌ Échec en {generation_time:.3f}s")

        # Statistiques de performance
        if times:
            print(f"\n📊 STATISTIQUES DE PERFORMANCE:")
            print(f"   Temps moyen: {statistics.mean(times):.3f}s")
            print(f"   Temps médian: {statistics.median(times):.3f}s")
            print(f"   Temps min: {min(times):.3f}s")
            print(f"   Temps max: {max(times):.3f}s")

            if len(times) > 1:
                print(f"   Écart-type: {statistics.stdev(times):.3f}s")

        if prompt_lengths:
            print(f"\n📏 STATISTIQUES DE LONGUEUR:")
            print(f"   Longueur moyenne: {statistics.mean(prompt_lengths):.0f} caractères")
            print(f"   Longueur médiane: {statistics.median(prompt_lengths):.0f} caractères")
            print(
                f"   Consistance: {(1 - statistics.stdev(prompt_lengths) / statistics.mean(prompt_lengths)) * 100:.1f}%")

        # Test de différents modules
        print(f"\n🎯 Test différents modules SCR...")
        modules_test = [SCRModule.SPREAD, SCRModule.EQUITY, SCRModule.INTEREST_RATE]
        module_times = {}

        for module in modules_test:
            config.scr_module = module

            start_time = time.time()
            result = generator.generate_optimized_prompt(config)
            end_time = time.time()

            module_times[module.value] = end_time - start_time
            print(f"   {module.value}: {module_times[module.value]:.3f}s")

        # Test mémoire (basique)
        print(f"\n💾 Test utilisation mémoire...")
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   Mémoire utilisée: {memory_mb:.1f} MB")

        # Test base de données
        print(f"\n🗄️ Test base de données...")
        stats = generator.get_statistics()
        db_size = stats['system_info']['database_size_mb']
        print(f"   Taille DB: {db_size:.2f} MB")
        print(f"   Documents: {stats['total_documents']}")

        generator.close()

        # Évaluation finale
        avg_time = statistics.mean(times) if times else 0
        if avg_time < 1.0:
            print(f"\n🏆 PERFORMANCE EXCELLENTE (< 1s)")
        elif avg_time < 3.0:
            print(f"\n✅ PERFORMANCE CORRECTE (< 3s)")
        else:
            print(f"\n⚠️ PERFORMANCE À AMÉLIORER (> 3s)")

        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False