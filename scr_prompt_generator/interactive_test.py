# ==========================================
# 5. TEST INTERACTIF COMPLET
# Fichier: interactive_test.py
# ==========================================

def interactive_full_test():
    """Test interactif complet pour validation utilisateur"""
    print("🎮 TEST INTERACTIF COMPLET")
    print("=" * 35)
    print("Ce test vous guide à travers toutes les fonctionnalités.")
    print()

    try:
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig, DocumentSource
        from src.config import AIProvider, ExpertiseLevel, SCRModule, DocumentType

        # Initialisation
        print("1️⃣ Initialisation du système...")
        generator = SCRPromptGenerator()
        print("✅ Système initialisé")

        # Menu principal
        while True:
            print(f"\n🎯 QUE VOULEZ-VOUS TESTER?")
            print("1. Génération de prompt")
            print("2. Ajout de document")
            print("3. Statistiques détaillées")
            print("4. Comparaison multi-IA")
            print("5. Test de performance")
            print("6. Tout tester automatiquement")
            print("0. Quitter")

            choice = input(f"\nVotre choix (0-6): ").strip()

            if choice == "0":
                break
            elif choice == "1":
                test_prompt_generation_interactive(generator)
            elif choice == "2":
                test_document_addition_interactive(generator)
            elif choice == "3":
                test_detailed_stats(generator)
            elif choice == "4":
                test_ai_comparison_interactive(generator)
            elif choice == "5":
                mini_performance_test(generator)
            elif choice == "6":
                auto_test_all(generator)
            else:
                print("❌ Choix invalide")

        generator.close()
        print(f"\n👋 Test terminé. Merci!")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")


def test_prompt_generation_interactive(generator):
    """Test de génération de prompt interactif"""
    print(f"\n🤖 TEST GÉNÉRATION DE PROMPT")
    print("-" * 30)

    # Sélection IA
    ais = [AIProvider.CLAUDE_SONNET_4, AIProvider.GPT_4, AIProvider.GEMINI_PRO]
    print("Sélectionnez une IA:")
    for i, ai in enumerate(ais, 1):
        print(f"  {i}. {ai.value}")

    ai_choice = input("Choix (1-3) [1]: ").strip() or "1"
    selected_ai = ais[int(ai_choice) - 1]

    # Sélection niveau
    levels = [ExpertiseLevel.JUNIOR, ExpertiseLevel.CONFIRMED, ExpertiseLevel.EXPERT]
    print(f"\nSélectionnez un niveau:")
    for i, level in enumerate(levels, 1):
        print(f"  {i}. {level.value}")

    level_choice = input("Choix (1-3) [3]: ").strip() or "3"
    selected_level = levels[int(level_choice) - 1]

    # Sélection module
    modules = [SCRModule.SPREAD, SCRModule.EQUITY, SCRModule.INTEREST_RATE]
    print(f"\nSélectionnez un module:")
    for i, module in enumerate(modules, 1):
        print(f"  {i}. {module.value}")

    module_choice = input("Choix (1-3) [1]: ").strip() or "1"
    selected_module = modules[int(module_choice) - 1]

    # Génération
    print(f"\n⏳ Génération en cours...")
    config = PromptConfig(
        ai_provider=selected_ai,
        expertise_level=selected_level,
        scr_module=selected_module
    )

    result = generator.generate_optimized_prompt(config)

    if result['success']:
        print(f"✅ Prompt généré!")
        print(f"   Longueur: {len(result['prompt'])} caractères")
        print(f"   Mots: {len(result['prompt'].split())}")

        # Aperçu
        show_preview = input(f"\nVoir un aperçu? (o/N): ").strip().lower()
        if show_preview in ['o', 'oui']:
            print(f"\n📄 APERÇU (300 premiers caractères):")
            print("-" * 40)
            print(result['prompt'][:300] + "...")
            print("-" * 40)

        # Sauvegarde
        save = input(f"\nSauvegarder dans un fichier? (o/N): ").strip().lower()
        if save in ['o', 'oui']:
            filename = input("Nom du fichier [prompt_test.txt]: ").strip() or "prompt_test.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result['prompt'])
                print(f"✅ Sauvegardé dans {filename}")
            except Exception as e:
                print(f"❌ Erreur sauvegarde: {e}")
    else:
        print(f"❌ Échec de génération")


def test_document_addition_interactive(generator):
    """Test d'ajout de document interactif"""
    print(f"\n📄 TEST AJOUT DE DOCUMENT")
    print("-" * 25)

    print("1. Créer un document de test")
    print("2. Ajouter un fichier existant")

    choice = input("Choix (1-2) [1]: ").strip() or "1"

    if choice == "1":
        # Créer document de test
        import tempfile
        test_content = """
        <html><head><title>Test SCR</title></head>
        <body>
        <h1>Test Article 180</h1>
        <p>SCR de spread selon Article 180 du Règlement délégué.</p>
        <p>Facteur de stress BBB: 2.5% par an de duration.</p>
        </body></html>
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file = f.name

        print(f"📝 Document de test créé")

        success = generator.add_document_source(
            file_path_or_url=temp_file,
            doc_type=DocumentType.EIOPA_GUIDELINES,
            scr_modules=[SCRModule.SPREAD],
            title="Document de test interactif"
        )

        if success:
            print("✅ Document ajouté avec succès!")
        else:
            print("❌ Échec ajout document")

        # Nettoyage
        import os
        os.unlink(temp_file)

    else:
        # Fichier existant
        filepath = input("Chemin du fichier: ").strip()
        if filepath:
            print("⏳ Traitement en cours...")
            # Traitement simplifié pour la démo
            print("✅ Fonctionnalité disponible via CLI: python cli.py add-doc")


def test_detailed_stats(generator):
    """Test des statistiques détaillées"""
    print(f"\n📊 STATISTIQUES DÉTAILLÉES")
    print("-" * 25)

    stats = generator.get_statistics()

    print(f"Documents totaux: {stats['total_documents']}")

    if stats.get('documents_by_type'):
        print(f"\nPar type:")
        for doc_type, count in stats['documents_by_type'].items():
            print(f"  • {doc_type}: {count}")

    if stats.get('documents_by_module'):
        print(f"\nPar module SCR:")
        for module, count in stats['documents_by_module'].items():
            print(f"  • {module}: {count}")

    print(f"\nTaille base: {stats['system_info']['database_size_mb']:.2f} MB")
    print(f"Répertoire: {stats['system_info']['data_directory']}")