#!/usr/bin/env python3
# ==========================================
# INTERFACE LIGNE DE COMMANDE - cli.py
# SCR Prompt Generator
# ==========================================

import argparse
import sys
import os
from pathlib import Path
from datetime import date, datetime


def create_cli():
    """Création de l'interface CLI"""
    parser = argparse.ArgumentParser(
        description="Générateur de prompts SCR Solvabilité 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLES D'UTILISATION:

  # Génération d'un prompt SCR spread pour Claude
  python cli.py generate --ai claude-sonnet-4 --level expert --module spread

  # Ajout d'un document réglementaire  
  python cli.py add-doc --file docs/reglement.pdf --type regulation_eu --modules spread,equity

  # Traitement en lot depuis un fichier YAML
  python cli.py batch --config batch_config.yaml

  # Statistiques de la base de connaissances
  python cli.py stats

  # Génération avec sauvegarde
  python cli.py generate --ai claude-sonnet-4 --level expert --module spread --output prompt_spread.txt

  # Recherche de documents
  python cli.py search --query "Article 180" --module spread

  # Validation de la santé du système
  python cli.py health
        """
    )

    # Options globales
    parser.add_argument('--data-dir', default='./data', help='Répertoire des données')
    parser.add_argument('--db-path', default='./data/scr_knowledge.db', help='Base de données')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
    parser.add_argument('--quiet', '-q', action='store_true', help='Mode silencieux')

    # Sous-commandes
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Commande: generate
    gen_parser = subparsers.add_parser('generate', help='Générer un prompt optimisé')
    gen_parser.add_argument('--ai', required=True,
                            choices=['claude-sonnet-4', 'claude-opus-4', 'gpt-4', 'gpt-4-turbo', 'gemini-pro'],
                            help='Fournisseur IA cible')
    gen_parser.add_argument('--level', required=True,
                            choices=['junior', 'confirmed', 'expert', 'regulation_specialist'],
                            help='Niveau d\'expertise')
    gen_parser.add_argument('--module', required=True,
                            choices=['spread', 'interest_rate', 'equity', 'currency', 'concentration',
                                     'market_global', 'counterparty', 'operational', 'life', 'non_life'],
                            help='Module SCR')
    gen_parser.add_argument('--language', default='fr', choices=['fr', 'en'], help='Langue')
    gen_parser.add_argument('--max-length', type=int, default=3000, help='Longueur max (mots)')
    gen_parser.add_argument('--output', '-o', help='Fichier de sortie')
    gen_parser.add_argument('--show-metadata', action='store_true', help='Afficher métadonnées')
    gen_parser.add_argument('--show-recommendations', action='store_true', help='Afficher recommandations')

    # Commande: add-doc
    doc_parser = subparsers.add_parser('add-doc', help='Ajouter un document source')
    doc_parser.add_argument('--file', required=True, help='Chemin fichier ou URL')
    doc_parser.add_argument('--type', required=True,
                            choices=['regulation_eu', 'directive', 'eiopa_guidelines',
                                     'technical_standards', 'industry_paper', 'internal_doc', 'academic_paper'],
                            help='Type de document')
    doc_parser.add_argument('--modules', required=True, help='Modules SCR (ex: spread,equity)')
    doc_parser.add_argument('--title', help='Titre du document')
    doc_parser.add_argument('--url', help='URL source')
    doc_parser.add_argument('--reliability', type=float, default=0.8, help='Score fiabilité (0-1)')
    doc_parser.add_argument('--language', default='fr', help='Langue du document')
    doc_parser.add_argument('--date', help='Date de publication (YYYY-MM-DD)')

    # Commande: batch
    batch_parser = subparsers.add_parser('batch', help='Traitement en lot')
    batch_parser.add_argument('--config', required=True, help='Fichier YAML de configuration')
    batch_parser.add_argument('--dry-run', action='store_true', help='Simulation sans traitement')

    # Commande: stats
    stats_parser = subparsers.add_parser('stats', help='Statistiques de la base')
    stats_parser.add_argument('--detailed', action='store_true', help='Statistiques détaillées')
    stats_parser.add_argument('--export', help='Export des stats (JSON)')

    # Commande: search
    search_parser = subparsers.add_parser('search', help='Rechercher des documents')
    search_parser.add_argument('--query', help='Requête de recherche')
    search_parser.add_argument('--module', choices=['spread', 'interest_rate', 'equity', 'currency',
                                                    'concentration', 'counterparty', 'operational'],
                               help='Module SCR à filtrer')
    search_parser.add_argument('--type', choices=['regulation_eu', 'directive', 'eiopa_guidelines'],
                               help='Type de document à filtrer')
    search_parser.add_argument('--min-reliability', type=float, default=0.0, help='Fiabilité minimum')
    search_parser.add_argument('--limit', type=int, default=10, help='Nombre max de résultats')

    # Commande: export
    export_parser = subparsers.add_parser('export', help='Exporter la base de connaissances')
    export_parser.add_argument('--output', required=True, help='Fichier de sortie')
    export_parser.add_argument('--format', choices=['json', 'csv', 'yaml'], default='json', help='Format')

    # Commande: health
    health_parser = subparsers.add_parser('health', help='Vérifier la santé du système')
    health_parser.add_argument('--fix', action='store_true', help='Tenter de corriger les problèmes')

    # Commande: init
    init_parser = subparsers.add_parser('init', help='Initialiser un nouveau projet')
    init_parser.add_argument('--create-sample-config', action='store_true',
                             help='Créer un fichier de config exemple')
    init_parser.add_argument('--force', action='store_true', help='Forcer la réinitialisation')

    return parser


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Configuration du logging selon le niveau"""
    import logging

    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    """Point d'entrée principal du CLI"""
    parser = create_cli()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Configuration du logging
    setup_logging(args.verbose, args.quiet)

    try:
        # Import des modules nécessaires
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig
        from src.config import AIProvider, ExpertiseLevel, SCRModule, DocumentType

        # Dispatch des commandes
        if args.command == 'generate':
            handle_generate(args)
        elif args.command == 'add-doc':
            handle_add_doc(args)
        elif args.command == 'batch':
            handle_batch(args)
        elif args.command == 'stats':
            handle_stats(args)
        elif args.command == 'search':
            handle_search(args)
        elif args.command == 'export':
            handle_export(args)
        elif args.command == 'health':
            handle_health(args)
        elif args.command == 'init':
            handle_init(args)

    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par l'utilisateur")
        sys.exit(1)
    except ImportError as e:
        print(f"❌ ERREUR D'IMPORT: {e}")
        print("💡 Vérifiez que vous êtes dans le bon répertoire et que les fichiers existent")
        print("🔧 Essayez: python create_all_files.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def handle_generate(args):
    """Gestion de la commande generate - VERSION CORRIGÉE"""
    from src.main import SCRPromptGenerator
    from src.knowledge.models import PromptConfig
    from src.config import AIProvider, ExpertiseLevel, SCRModule

    print(f"🚀 Génération prompt {args.module} pour {args.ai} (niveau {args.level})")

    # Conversion des arguments - VERSION CORRIGÉE
    try:
        # Mapping des noms d'IA
        ai_mapping = {
            'claude-sonnet-4': AIProvider.CLAUDE_SONNET_4,
            'claude-opus-4': AIProvider.CLAUDE_OPUS_4,
            'gpt-4': AIProvider.GPT_4,
            'gpt-4-turbo': AIProvider.GPT_4_TURBO,
            'gemini-pro': AIProvider.GEMINI_PRO
        }

        level_mapping = {
            'junior': ExpertiseLevel.JUNIOR,
            'confirmed': ExpertiseLevel.CONFIRMED,
            'expert': ExpertiseLevel.EXPERT,
            'regulation_specialist': ExpertiseLevel.REGULATION_SPECIALIST
        }

        module_mapping = {
            'spread': SCRModule.SPREAD,
            'interest_rate': SCRModule.INTEREST_RATE,
            'equity': SCRModule.EQUITY,
            'currency': SCRModule.CURRENCY,
            'concentration': SCRModule.CONCENTRATION,
            'market_global': SCRModule.MARKET_GLOBAL,
            'counterparty': SCRModule.COUNTERPARTY,
            'operational': SCRModule.OPERATIONAL,
            'life': SCRModule.LIFE,
            'non_life': SCRModule.NON_LIFE
        }

        ai_provider = ai_mapping.get(args.ai)
        expertise_level = level_mapping.get(args.level)
        scr_module = module_mapping.get(args.module)

        if not ai_provider:
            print(f"❌ IA non supportée: {args.ai}")
            print(f"💡 IA disponibles: {', '.join(ai_mapping.keys())}")
            return

        if not expertise_level:
            print(f"❌ Niveau non supporté: {args.level}")
            print(f"💡 Niveaux disponibles: {', '.join(level_mapping.keys())}")
            return

        if not scr_module:
            print(f"❌ Module non supporté: {args.module}")
            print(f"💡 Modules disponibles: {', '.join(module_mapping.keys())}")
            return

    except Exception as e:
        print(f"❌ Erreur conversion: {e}")
        return

    config = PromptConfig(
        ai_provider=ai_provider,
        expertise_level=expertise_level,
        scr_module=scr_module,
        language=args.language,
        max_length=args.max_length
    )

    try:
        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            result = generator.generate_optimized_prompt(config)

            if result['success']:
                if args.output:
                    # Sauvegarde dans fichier
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(result['prompt'])
                    print(f"✅ Prompt sauvegardé: {args.output}")
                else:
                    # Affichage console
                    print("\n" + "=" * 80)
                    print("PROMPT OPTIMISÉ")
                    print("=" * 80)
                    print(result['prompt'])
                    print("=" * 80)

                # Métadonnées
                metadata = result['metadata']
                print(f"\n📊 INFORMATIONS:")
                print(f"   • Longueur: {metadata['generation_info']['prompt_length_chars']} caractères")
                print(f"   • Mots: {metadata['generation_info']['prompt_length_words']}")
                print(f"   • Tokens estimés: {metadata['generation_info']['estimated_tokens']:.0f}")
                print(f"   • Sources utilisées: {metadata['knowledge_base_stats']['relevant_documents']}")
                print(f"   • Temps génération: {metadata['generation_info']['generation_time_seconds']:.2f}s")
                print(f"   • Score qualité: {result.get('quality_score', 0):.2f}/1.0")

                if args.show_metadata:
                    print(f"\n📋 MÉTADONNÉES COMPLÈTES:")
                    import json
                    print(json.dumps(metadata, indent=2, ensure_ascii=False))

                # Recommandations
                if args.show_recommendations or not args.output:
                    if result['usage_recommendations']:
                        print(f"\n💡 RECOMMANDATIONS D'UTILISATION:")
                        for rec in result['usage_recommendations']:
                            print(f"   {rec}")

                # Instructions d'utilisation
                print(f"\n🎯 COMMENT UTILISER CE PROMPT:")
                print(f"   1. Copiez le prompt ci-dessus")
                print(f"   2. Ouvrez {args.ai} (Claude, ChatGPT, etc.)")
                print(f"   3. Collez le prompt et lancez la génération")
                print(f"   4. Pas besoin de clé API dans ce système!")

            else:
                print(f"❌ Échec de génération: {result.get('error', 'Erreur inconnue')}")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_add_doc(args):
    """Gestion de la commande add-doc"""
    from src.main import SCRPromptGenerator
    from src.config import DocumentType, SCRModule

    print(f"📄 Ajout document: {Path(args.file).name}")

    # Conversion des arguments
    try:
        doc_type = DocumentType(args.type.upper())
        modules = [SCRModule(m.strip().upper()) for m in args.modules.split(',')]
    except ValueError as e:
        print(f"❌ Valeur invalide: {e}")
        return

    # Métadonnées
    metadata = {}
    if args.title:
        metadata['title'] = args.title
    if args.url:
        metadata['url'] = args.url
    if args.reliability:
        metadata['reliability_score'] = args.reliability
    if args.language:
        metadata['language'] = args.language
    if args.date:
        try:
            metadata['publication_date'] = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"⚠️ Format de date invalide: {args.date} (attendu: YYYY-MM-DD)")

    # Vérification du fichier
    if not args.file.startswith(('http://', 'https://')):
        if not Path(args.file).exists():
            print(f"❌ Fichier non trouvé: {args.file}")
            return

        file_size = Path(args.file).stat().st_size / (1024 * 1024)  # MB
        if file_size > 100:
            print(f"⚠️ Fichier volumineux: {file_size:.1f}MB")

    try:
        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            print("⏳ Traitement en cours...")

            success = generator.add_document_source(
                file_path_or_url=args.file,
                doc_type=doc_type,
                scr_modules=modules,
                **metadata
            )

            if success:
                print("✅ Document ajouté avec succès!")

                # Affichage des statistiques mises à jour
                stats = generator.get_statistics()
                print(f"📊 Total documents: {stats['total_documents']}")
            else:
                print("❌ Erreur lors de l'ajout du document")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_batch(args):
    """Gestion de la commande batch"""
    if not Path(args.config).exists():
        print(f"❌ Fichier de configuration non trouvé: {args.config}")
        return

    try:
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except ImportError:
        print("❌ PyYAML requis pour les fichiers de configuration")
        print("💡 Installez avec: pip install pyyaml")
        return
    except Exception as e:
        print(f"❌ Erreur lecture configuration: {e}")
        return

    documents = config.get('documents', [])
    if not documents:
        print("❌ Aucun document dans la configuration")
        return

    print(f"📦 Traitement en lot: {len(documents)} documents")

    if args.dry_run:
        print("🔍 MODE SIMULATION - Aucun traitement réel")
        for i, doc_config in enumerate(documents, 1):
            print(f"   {i}. {doc_config.get('file_path', 'N/A')} -> {doc_config.get('doc_type', 'N/A')}")
        return

    try:
        from src.main import SCRPromptGenerator

        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            results = generator.batch_process_documents(documents)

            success_count = sum(1 for r in results.values() if r)
            total_count = len(results)

            print(f"\n📊 RÉSULTATS: {success_count}/{total_count} documents traités avec succès")

            for file_path, success in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {Path(file_path).name}")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_stats(args):
    """Gestion de la commande stats"""
    try:
        from src.main import SCRPromptGenerator

        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            stats = generator.get_statistics()

            print("📊 STATISTIQUES SCR PROMPT GENERATOR")
            print("=" * 50)

            # Statistiques principales
            print(f"\n📄 Base de connaissances:")
            print(f"   • Total documents: {stats['total_documents']}")
            print(f"   • Base de données: {stats['system_info']['database_size_mb']:.2f} MB")

            if args.detailed:
                # Statistiques détaillées
                if stats.get('documents_by_type'):
                    print(f"\n📑 Documents par type:")
                    for doc_type, count in stats['documents_by_type'].items():
                        print(f"   • {doc_type}: {count}")

                if stats.get('documents_by_module'):
                    print(f"\n🎯 Documents par module SCR:")
                    for module, count in stats['documents_by_module'].items():
                        print(f"   • {module}: {count}")

                if stats.get('concepts_by_module'):
                    print(f"\n💡 Concepts extraits:")
                    total_concepts = sum(stats['concepts_by_module'].values())
                    print(f"   • Total: {total_concepts}")
                    for module, count in stats['concepts_by_module'].items():
                        print(f"   • {module}: {count}")

                # Informations système
                session_stats = stats.get('session_stats', {})
                if session_stats:
                    print(f"\n⚙️ Session courante:")
                    print(f"   • Documents traités: {session_stats.get('documents_processed', 0)}")
                    print(f"   • Prompts générés: {session_stats.get('prompts_generated', 0)}")

                    uptime = stats['system_info'].get('uptime_seconds', 0)
                    if uptime > 0:
                        print(f"   • Uptime: {uptime:.1f}s")

                # Capacités
                capabilities = stats.get('capabilities', {})
                if capabilities:
                    print(f"\n🔧 Capacités système:")
                    print(f"   • IA supportées: {len(capabilities.get('supported_ai_providers', []))}")
                    print(f"   • Modules SCR: {len(capabilities.get('supported_scr_modules', []))}")
                    print(f"   • Types documents: {len(capabilities.get('supported_document_types', []))}")

            print(f"\n🕒 Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Export optionnel
            if args.export:
                import json
                with open(args.export, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
                print(f"📁 Statistiques exportées: {args.export}")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_search(args):
    """Gestion de la commande search"""
    try:
        from src.main import SCRPromptGenerator
        from src.config import SCRModule, DocumentType

        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            # Préparation des filtres
            scr_modules = [SCRModule(args.module.upper())] if args.module else None
            doc_types = [DocumentType(args.type.upper())] if args.type else None

            # Recherche
            results = generator.search_documents(
                query=args.query,
                scr_modules=scr_modules,
                doc_types=doc_types,
                min_reliability=args.min_reliability
            )

            # Limitation des résultats
            results = results[:args.limit]

            print(f"🔍 RÉSULTATS DE RECHERCHE")
            print("=" * 40)

            if not results:
                print("Aucun document trouvé.")
                return

            print(f"Trouvé {len(results)} document(s):")

            for i, doc in enumerate(results, 1):
                print(f"\n{i}. {doc.title}")
                print(f"   Type: {doc.doc_type.value}")
                print(f"   Modules: {', '.join([m.value for m in doc.scr_modules])}")
                print(f"   Fiabilité: {doc.reliability_score:.1f}")
                if doc.regulatory_articles:
                    print(f"   Articles: {', '.join(doc.regulatory_articles[:5])}")
                if doc.url:
                    print(f"   URL: {doc.url}")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_export(args):
    """Gestion de la commande export"""
    try:
        from src.main import SCRPromptGenerator

        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            print(f"📤 Export en cours vers {args.output}...")

            success = generator.export_knowledge_base(args.output, args.format)

            if success:
                print(f"✅ Export réussi: {args.output}")

                # Affichage de la taille du fichier
                file_size = Path(args.output).stat().st_size
                if file_size > 1024 * 1024:
                    print(f"📊 Taille: {file_size / (1024 * 1024):.1f} MB")
                else:
                    print(f"📊 Taille: {file_size / 1024:.1f} KB")
            else:
                print("❌ Échec de l'export")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_health(args):
    """Gestion de la commande health"""
    try:
        from src.main import SCRPromptGenerator

        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            print("🏥 DIAGNOSTIC DE SANTÉ DU SYSTÈME")
            print("=" * 40)

            health = generator.validate_system_health()

            # Statut global
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'unhealthy': '❌',
                'critical': '🚨'
            }

            emoji = status_emoji.get(health['overall_status'], '❓')
            print(f"\n{emoji} Statut global: {health['overall_status'].upper()}")

            # Vérifications détaillées
            if health.get('checks'):
                print(f"\n🔍 Vérifications:")
                for check, result in health['checks'].items():
                    if isinstance(result, str):
                        status = "✅" if result == 'ok' else "❌"
                        print(f"   {status} {check}: {result}")
                    else:
                        print(f"   ℹ️ {check}: {result}")

            # Avertissements
            if health.get('warnings'):
                print(f"\n⚠️ Avertissements:")
                for warning in health['warnings']:
                    print(f"   • {warning}")

            # Erreurs
            if health.get('errors'):
                print(f"\n❌ Erreurs:")
                for error in health['errors']:
                    print(f"   • {error}")

            # Tentative de correction
            if args.fix and health['overall_status'] != 'healthy':
                print(f"\n🔧 Tentative de correction...")

                # Créer les répertoires manquants
                Path(args.data_dir).mkdir(exist_ok=True)
                Path(args.data_dir + "/documents").mkdir(exist_ok=True)

                print("✅ Répertoires créés/vérifiés")

                # Nouvelle vérification
                health_after = generator.validate_system_health()
                if health_after['overall_status'] != health['overall_status']:
                    print(f"✅ Amélioration: {health_after['overall_status']}")
                else:
                    print("⚠️ Certains problèmes nécessitent une intervention manuelle")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def handle_init(args):
    """Gestion de la commande init"""
    print("🔧 Initialisation d'un nouveau projet SCR")

    # Création de la structure de base
    directories = [
        args.data_dir,
        f"{args.data_dir}/documents",
        "./logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire créé: {directory}")

    # Création d'un fichier de config exemple
    if args.create_sample_config:
        create_sample_config()
        print("✅ Fichier sample_config.yaml créé")

    # Test d'initialisation
    try:
        from src.main import SCRPromptGenerator

        with SCRPromptGenerator(args.data_dir, args.db_path) as generator:
            stats = generator.get_statistics()
            print(f"✅ Système initialisé: {stats['total_documents']} documents")

    except Exception as e:
        print(f"⚠️ Problème d'initialisation: {e}")
        print("💡 Essayez: python create_all_files.py")

    print(f"\n🎉 Initialisation terminée!")
    print(f"💡 Prochaines étapes:")
    print(f"   1. python cli.py add-doc --file votre_document.pdf --type regulation_eu --modules spread")
    print(f"   2. python cli.py generate --ai claude-sonnet-4 --level expert --module spread")


def create_sample_config():
    """Création d'un fichier de configuration exemple"""
    sample_config = {
        'documents': [
            {
                'file_path': './data/documents/reglement_delegue_2015_35.pdf',
                'doc_type': 'regulation_eu',
                'scr_modules': ['spread', 'interest_rate', 'equity'],
                'metadata': {
                    'title': 'Règlement délégué (UE) 2015/35',
                    'url': 'https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A32015R0035',
                    'language': 'fr',
                    'reliability_score': 1.0
                }
            },
            {
                'file_path': 'https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-5796_en',
                'doc_type': 'eiopa_guidelines',
                'scr_modules': ['spread'],
                'metadata': {
                    'title': 'EIOPA Guidelines on Spread Risk',
                    'reliability_score': 0.9,
                    'language': 'en'
                }
            }
        ]
    }

    try:
        import yaml
        with open('sample_config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True)
    except ImportError:
        # Fallback JSON si PyYAML non disponible
        import json
        with open('sample_config.json', 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        print("⚠️ PyYAML non disponible, fichier JSON créé à la place")


if __name__ == "__main__":
    main()