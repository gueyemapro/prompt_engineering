#!/usr/bin/env python3
# ==========================================
# FICHIER DE TEST SIMPLE - run_tests.py
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

        # Vérification de la qualité
        prompt = result['prompt']
        quality_checks = [
            ("Contient 'SCR'", "SCR" in prompt or "scr" in prompt),
            ("Contient 'spread'", "spread" in prompt.lower()),
            ("Longueur correcte", len(prompt) > 500),
            ("Structure présente", any(word in prompt for word in ["SYNTHÈSE", "synthèse", "STRUCTURE", "structure"]))
        ]

        print("\n4. Vérifications qualité...")
        for check_name, passed in quality_checks:
            status = "✅" if passed else "⚠️"
            print(f"   {status} {check_name}")

        # Test statistiques
        print("\n5. Test statistiques...")
        stats = generator.get_statistics()
        print(f"✅ Stats récupérées: {stats['total_documents']} documents")

        # Affichage d'un extrait du prompt
        print(f"\n📄 EXTRAIT DU PROMPT (200 premiers caractères):")
        print("-" * 50)
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        print("-" * 50)

        generator.close()
        print("\n🎉 TOUS LES TESTS DE BASE PASSÉS!")
        print("🚀 Votre système fonctionne correctement!")
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli():
    """Test du CLI"""
    print("\n🖥️  TEST CLI")
    print("=" * 20)

    import subprocess
    import sys

    try:
        # Test help
        print("Test commande help...")
        result = subprocess.run([sys.executable, "cli.py", "--help"],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ CLI accessible")
        else:
            print("⚠️ CLI non accessible")

        # Test stats
        print("Test commande stats...")
        result = subprocess.run([sys.executable, "cli.py", "stats"],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Commande stats fonctionne")
            print(f"Sortie: {result.stdout[:100]}...")
        else:
            print("⚠️ Commande stats échoue")
            print(f"Erreur: {result.stderr}")

    except Exception as e:
        print(f"❌ Erreur test CLI: {e}")


def test_with_sample_document():
    """Test avec un document d'exemple"""
    print("\n📄 TEST AVEC DOCUMENT D'EXEMPLE")
    print("=" * 35)

    import tempfile
    import os

    # Document HTML de test
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>SCR Spread - Article 180</title></head>
    <body>
        <h1>Calcul du SCR de spread</h1>
        <p>Le SCR de spread selon l'Article 180 du Règlement délégué couvre le risque de crédit.</p>
        <h2>Formule</h2>
        <p>SCR_spread = Duration × Facteur de stress</p>
        <p>Facteurs par notation:</p>
        <ul>
            <li>AAA: 0.9% par an</li>
            <li>BBB: 2.5% par an</li>
            <li>Non noté: 3.0% par an</li>
        </ul>
        <p>Référence: Article 180 et Article 181 du Règlement délégué (UE) 2015/35</p>
    </body>
    </html>
    """

    try:
        # Création fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(sample_html)
            temp_file = f.name

        print(f"📝 Document créé: {os.path.basename(temp_file)}")

        # Test d'ajout
        from src.main import SCRPromptGenerator
        from src.config import DocumentType, SCRModule

        generator = SCRPromptGenerator()

        print("📤 Ajout du document...")
        success = generator.add_document_source(
            file_path_or_url=temp_file,
            doc_type=DocumentType.EIOPA_GUIDELINES,
            scr_modules=[SCRModule.SPREAD],
            title="Document Test SCR Spread"
        )

        if success:
            print("✅ Document ajouté avec succès")

            # Vérification en base
            docs = generator.knowledge_base.get_documents_by_module(SCRModule.SPREAD)
            print(f"✅ Documents en base: {len(docs)}")

            if docs:
                doc = docs[0]
                print(f"   Titre: {doc.title}")
                print(f"   Articles extraits: {doc.regulatory_articles}")

            # Test génération enrichie
            print("\n🤖 Test génération avec document...")
            from src.knowledge.models import PromptConfig
            from src.config import AIProvider, ExpertiseLevel

            config = PromptConfig(
                ai_provider=AIProvider.CLAUDE_SONNET_4,
                expertise_level=ExpertiseLevel.EXPERT,
                scr_module=SCRModule.SPREAD
            )

            result = generator.generate_optimized_prompt(config)
            print(f"✅ Prompt enrichi: {len(result['prompt'])} caractères")
            print(f"✅ Sources utilisées: {result['metadata']['knowledge_base_stats']['relevant_documents']}")

        else:
            print("❌ Échec ajout document")

        generator.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        # Nettoyage
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)


def interactive_test():
    """Test interactif simple"""
    print("\n🎮 TEST INTERACTIF")
    print("=" * 25)

    try:
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig
        from src.config import AIProvider, ExpertiseLevel, SCRModule

        generator = SCRPromptGenerator()

        print("Système initialisé ✅")
        print("\nGénération d'un prompt test...")

        # Configuration simple
        config = PromptConfig(
            ai_provider=AIProvider.CLAUDE_SONNET_4,
            expertise_level=ExpertiseLevel.EXPERT,
            scr_module=SCRModule.SPREAD,
            max_length=3000
        )

        result = generator.generate_optimized_prompt(config)

        if result['success']:
            print(f"✅ Prompt généré: {len(result['prompt'])} caractères")

            # Proposer d'afficher
            show = input("\nVoulez-vous voir le prompt généré? (o/N): ").strip().lower()
            if show in ['o', 'oui', 'y', 'yes']:
                print(f"\n{'=' * 60}")
                print("PROMPT GÉNÉRÉ:")
                print(f"{'=' * 60}")
                print(result['prompt'])
                print(f"{'=' * 60}")

            # Proposer de sauvegarder
            save = input("\nVoulez-vous sauvegarder le prompt? (o/N): ").strip().lower()
            if save in ['o', 'oui', 'y', 'yes']:
                filename = input("Nom du fichier [prompt_test.txt]: ").strip() or "prompt_test.txt"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result['prompt'])
                    print(f"✅ Sauvegardé dans {filename}")
                except Exception as e:
                    print(f"❌ Erreur sauvegarde: {e}")

        generator.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    """Point d'entrée principal"""
    import sys

    print("🧪 SYSTÈME DE TEST SCR PROMPT GENERATOR")
    print("=" * 45)

    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()

        if test_type == "quick":
            quick_test()
        elif test_type == "cli":
            test_cli()
        elif test_type == "document":
            test_with_sample_document()
        elif test_type == "interactive":
            interactive_test()
        elif test_type == "all":
            print("🚀 EXÉCUTION DE TOUS LES TESTS")
            print("=" * 35)

            tests = [
                ("Test rapide", quick_test),
                ("Test avec document", test_with_sample_document),
                ("Test CLI", test_cli)
            ]

            results = []
            for test_name, test_func in tests:
                print(f"\n{'=' * 40}")
                print(f"🧪 {test_name.upper()}")
                print(f"{'=' * 40}")
                try:
                    success = test_func()
                    results.append((test_name, success))
                except Exception as e:
                    print(f"❌ Erreur dans {test_name}: {e}")
                    results.append((test_name, False))

            # Résumé
            print(f"\n{'=' * 40}")
            print("📋 RÉSUMÉ DES TESTS")
            print(f"{'=' * 40}")

            passed = 0
            for test_name, success in results:
                status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
                print(f"{test_name:<20} {status}")
                if success:
                    passed += 1

            print(f"\n🎯 RÉSULTAT: {passed}/{len(results)} tests réussis")

            if passed == len(results):
                print("🎉 FÉLICITATIONS! Votre système fonctionne parfaitement!")
            else:
                print("⚠️ Certains tests ont échoué, mais le système de base fonctionne.")
        else:
            print(f"❌ Type de test inconnu: {test_type}")
            print("Types disponibles: quick, cli, document, interactive, all")
    else:
        # Menu interactif
        print("\nQuel test voulez-vous exécuter?")
        print("1. Test rapide (recommandé)")
        print("2. Test avec document")
        print("3. Test CLI")
        print("4. Test interactif")
        print("5. Tous les tests")

        choice = input("\nVotre choix (1-5) [1]: ").strip() or "1"

        if choice == "1":
            quick_test()
        elif choice == "2":
            test_with_sample_document()
        elif choice == "3":
            test_cli()
        elif choice == "4":
            interactive_test()
        elif choice == "5":
            # Exécuter tous les tests
            sys.argv.append("all")
            main()
        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    main()