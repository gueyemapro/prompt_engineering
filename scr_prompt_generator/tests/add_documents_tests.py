#!/usr/bin/env python3
# ==========================================
# SCRIPT DE TEST FONCTIONNEL
# Fichier: add_documents_test.py
# ==========================================

from src.main import SCRPromptGenerator
from src.config import DocumentType, SCRModule
from src.knowledge.models import PromptConfig
from src.config import AIProvider, ExpertiseLevel
import tempfile
import os


def test_add_document():
    """Test d'ajout de document qui fonctionne à coup sûr"""

    print("🧪 TEST D'AJOUT DE DOCUMENT")
    print("=" * 35)

    # Créer un document HTML réaliste sur le SCR de spread
    realistic_document = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Règlement délégué (UE) 2015/35 - SCR de spread</title>
        <meta name="description" content="Calcul du SCR de spread selon les Articles 175-181">
    </head>
    <body>
        <h1>CHAPITRE VII - SOUS-MODULE RISQUE DE SPREAD</h1>

        <h2>Article 175 - Périmètre du sous-module risque de spread</h2>
        <p>Le capital de solvabilité requis pour le risque de spread visé au point d) du deuxième alinéa 
        de l'article 105, paragraphe 5, de la directive 2009/138/CE est égal à ce qui suit:</p>

        <p><strong>SCR_spread = SCR_bonds + SCR_securitisation + SCR_cd</strong></p>

        <h2>Article 176 - Risque de spread sur les obligations et les prêts</h2>
        <p>Le capital de solvabilité requis pour le risque de spread sur les obligations et les prêts 
        SCR_bonds est égal à la perte des fonds propres de base qui résulterait d'une diminution 
        relative instantanée du facteur de stress_i de la valeur de chaque obligation ou prêt i.</p>

        <h3>Facteurs de stress par notation de crédit</h3>
        <table border="1">
            <tr>
                <th>Qualité de crédit</th>
                <th>Duration 1 an</th>
                <th>Duration 5 ans</th>
                <th>Duration 10 ans</th>
                <th>Duration 15 ans</th>
                <th>Duration 20 ans</th>
            </tr>
            <tr>
                <td>0 (AAA)</td>
                <td>0,9%</td>
                <td>4,5%</td>
                <td>9,0%</td>
                <td>13,5%</td>
                <td>18,0%</td>
            </tr>
            <tr>
                <td>1 (AA)</td>
                <td>1,1%</td>
                <td>5,5%</td>
                <td>11,0%</td>
                <td>16,5%</td>
                <td>22,0%</td>
            </tr>
            <tr>
                <td>2 (A)</td>
                <td>1,4%</td>
                <td>7,0%</td>
                <td>14,0%</td>
                <td>21,0%</td>
                <td>28,0%</td>
            </tr>
            <tr>
                <td>3 (BBB)</td>
                <td>2,5%</td>
                <td>12,5%</td>
                <td>25,0%</td>
                <td>37,5%</td>
                <td>50,0%</td>
            </tr>
            <tr>
                <td>4 (BB)</td>
                <td>4,5%</td>
                <td>22,5%</td>
                <td>45,0%</td>
                <td>67,5%</td>
                <td>90,0%</td>
            </tr>
            <tr>
                <td>5 (B)</td>
                <td>7,5%</td>
                <td>37,5%</td>
                <td>75,0%</td>
                <td>100,0%</td>
                <td>100,0%</td>
            </tr>
            <tr>
                <td>6 (CCC et moins)</td>
                <td>15,0%</td>
                <td>75,0%</td>
                <td>100,0%</td>
                <td>100,0%</td>
                <td>100,0%</td>
            </tr>
            <tr>
                <td>Non noté</td>
                <td>3,0%</td>
                <td>15,0%</td>
                <td>30,0%</td>
                <td>45,0%</td>
                <td>60,0%</td>
            </tr>
        </table>

        <h2>Article 180 - Facteur de risque</h2>
        <p>Le facteur de risque stress_i dépend de la duration modifiée de l'obligation ou du prêt i 
        exprimée en années (dur_i). La valeur dur_i ne peut jamais être inférieure à 1.</p>

        <p>Pour les obligations ou prêts à taux variable, dur_i est équivalent à la duration modifiée 
        d'une obligation ou d'un prêt à taux fixe de même échéance et dont les paiements de coupon 
        sont égaux au taux d'intérêt à terme.</p>

        <h2>Article 181 - Règles spéciales</h2>
        <h3>1. Obligations souveraines</h3>
        <p>Les expositions aux administrations centrales des États membres dans la devise de cet État membre 
        sont exemptées du choc de spread.</p>

        <h3>2. Duration minimale</h3>
        <p>La duration modifiée ne peut jamais être inférieure à 1 an pour le calcul du facteur de stress.</p>

        <h3>3. Plafonnement</h3>
        <p>Le choc de spread appliqué à une exposition ne peut excéder 100% de la valeur de cette exposition.</p>

        <h2>Exemple de calcul pratique</h2>
        <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0;">
            <h4>Cas pratique: Obligation corporate BBB</h4>
            <ul>
                <li><strong>Valeur nominale:</strong> 100 millions d'euros</li>
                <li><strong>Notation:</strong> BBB (qualité de crédit 3)</li>
                <li><strong>Duration modifiée:</strong> 8,2 ans</li>
            </ul>

            <p><strong>Calcul du facteur de stress:</strong></p>
            <p>Interpolation linéaire entre 5 ans (12,5%) et 10 ans (25,0%)</p>
            <p>Facteur = 12,5% + (8,2-5) × (25,0%-12,5%) / (10-5) = 20,5%</p>

            <p><strong>SCR de spread:</strong></p>
            <p>SCR = 100M€ × 20,5% = 20,5 millions d'euros</p>
        </div>

        <h2>Corrélations avec autres modules</h2>
        <p>Le SCR de spread est corrélé avec les autres sous-modules selon la matrice de corrélation 
        de l'Annexe IV. Notamment:</p>
        <ul>
            <li>Corrélation avec le module taux: 50% (révision 2025: 25%)</li>
            <li>Corrélation avec le module actions: 25%</li>
            <li>Corrélation avec le module change: 25%</li>
        </ul>

        <footer>
            <p><em>Source: Règlement délégué (UE) 2015/35 de la Commission du 10 octobre 2014</em></p>
            <p><em>Articles 175, 176, 180, 181 - Sous-module risque de spread</em></p>
        </footer>
    </body>
    </html>
    """

    try:
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(realistic_document)
            temp_file = f.name

        print(f"📝 Document de test créé: {os.path.basename(temp_file)}")

        # Initialiser le générateur
        with SCRPromptGenerator() as generator:

            print("📤 Ajout du document à la base de connaissances...")

            # Ajout du document
            success = generator.add_document_source(
                file_path_or_url=temp_file,
                doc_type=DocumentType.REGULATION_EU,  # Utilisation directe de l'enum
                scr_modules=[SCRModule.SPREAD, SCRModule.CONCENTRATION],  # Modules pertinents
                title="Règlement délégué (UE) 2015/35 - Articles 175-181 (SCR Spread)",
                url="https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A32015R0035",
                reliability_score=1.0,  # Maximum pour un règlement officiel
                language="fr"
            )

            if success:
                print("✅ Document ajouté avec succès!")

                # Vérification des statistiques
                stats = generator.get_statistics()
                print(f"📊 Statistiques mises à jour:")
                print(f"   • Total documents: {stats['total_documents']}")
                print(f"   • Taille base: {stats['system_info']['database_size_mb']:.2f} MB")

                # Vérification des documents par module
                spread_docs = generator.knowledge_base.get_documents_by_module(SCRModule.SPREAD)
                print(f"   • Documents SCR Spread: {len(spread_docs)}")

                if spread_docs:
                    doc = spread_docs[0]
                    print(f"   • Dernier document: {doc.title[:50]}...")
                    print(f"   • Articles extraits: {doc.regulatory_articles}")

                # Test de génération de prompt enrichi
                print(f"\n🤖 Test de génération de prompt enrichi...")

                config = PromptConfig(
                    ai_provider=AIProvider.CLAUDE_SONNET_4,
                    expertise_level=ExpertiseLevel.EXPERT,
                    scr_module=SCRModule.SPREAD,
                    max_length=4000
                )

                result = generator.generate_optimized_prompt(config)

                if result['success']:
                    print("✅ Prompt enrichi généré avec succès!")

                    metadata = result['metadata']
                    print(f"📊 Informations du prompt:")
                    print(f"   • Longueur: {metadata['generation_info']['prompt_length_chars']} caractères")
                    print(f"   • Mots: {metadata['generation_info']['prompt_length_words']}")
                    print(f"   • Sources utilisées: {metadata['knowledge_base_stats']['relevant_documents']}")
                    print(f"   • Score qualité: {result.get('quality_score', 0):.2f}/1.0")

                    # Sauvegarde du prompt enrichi
                    with open('../prompt_enrichi_avec_reglement.txt', 'w', encoding='utf-8') as f:
                        f.write(result['prompt'])
                        f.write(f"\n\n{'=' * 60}\n")
                        f.write("MÉTADONNÉES DE GÉNÉRATION\n")
                        f.write(f"{'=' * 60}\n")
                        f.write(f"Sources utilisées: {metadata['knowledge_base_stats']['relevant_documents']}\n")
                        f.write(f"Qualité: {result.get('quality_score', 0):.2f}/1.0\n")

                        if result.get('usage_recommendations'):
                            f.write(f"\nRecommandations d'utilisation:\n")
                            for rec in result['usage_recommendations']:
                                f.write(f"- {rec}\n")

                    print("✅ Prompt sauvegardé: prompt_enrichi_avec_reglement.txt")

                    # Aperçu du prompt
                    print(f"\n📄 APERÇU DU PROMPT ENRICHI (300 premiers caractères):")
                    print("-" * 60)
                    print(result['prompt'][:300] + "...")
                    print("-" * 60)

                    # Vérification de l'enrichissement
                    if "Article 175" in result['prompt'] or "Article 180" in result['prompt']:
                        print("🎯 SUCCÈS: Le prompt contient des références aux articles réglementaires!")

                    if "BBB" in result['prompt'] and "duration" in result['prompt'].lower():
                        print("🎯 SUCCÈS: Le prompt contient des éléments techniques spécifiques!")

                else:
                    print("❌ Erreur génération prompt enrichi")

            else:
                print("❌ Échec de l'ajout du document")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Nettoyage du fichier temporaire
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)
            print("🧹 Fichier temporaire nettoyé")


def test_multiple_documents():
    """Test d'ajout de plusieurs documents différents"""

    print(f"\n🧪 TEST D'AJOUT DE PLUSIEURS DOCUMENTS")
    print("=" * 45)

    # Documents de test avec différents contenus
    documents_test = [
        {
            'content': '''
            <html><head><title>EIOPA Guidelines Spread Risk</title></head>
            <body>
                <h1>Guidelines on the calibration of spread risk</h1>
                <p>These guidelines specify the methodology for calculating spread risk factors according to Article 176.</p>
                <p>The stress factors shall be applied to the modified duration of bonds and loans.</p>
                <p>Special treatment for government bonds: exemption for EU member state bonds in local currency.</p>
            </body></html>
            ''',
            'doc_type': DocumentType.EIOPA_GUIDELINES,
            'modules': [SCRModule.SPREAD],
            'title': 'EIOPA Guidelines on Spread Risk Calibration',
            'reliability': 0.95
        },
        {
            'content': '''
            <html><head><title>SCR Equity Risk</title></head>
            <body>
                <h1>SCR Equity - Type I and Type II</h1>
                <p>Type I equities: 39% shock (before symmetric adjustment)</p>
                <p>Type II equities: 49% shock</p>
                <p>Symmetric adjustment (dampener): ±17% range</p>
                <p>Long Term Equity Investment (LTEI): reduced capital charge under specific conditions</p>
            </body></html>
            ''',
            'doc_type': DocumentType.TECHNICAL_STANDARDS,
            'modules': [SCRModule.EQUITY],
            'title': 'Technical Standards on Equity Risk',
            'reliability': 0.9
        }
    ]

    with SCRPromptGenerator() as generator:

        for i, doc_info in enumerate(documents_test, 1):
            print(f"\n📄 Ajout document {i}/{len(documents_test)}: {doc_info['title']}")

            try:
                # Créer fichier temporaire
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(doc_info['content'])
                    temp_file = f.name

                # Ajouter à la base
                success = generator.add_document_source(
                    file_path_or_url=temp_file,
                    doc_type=doc_info['doc_type'],
                    scr_modules=doc_info['modules'],
                    title=doc_info['title'],
                    reliability_score=doc_info['reliability']
                )

                if success:
                    print(f"   ✅ Ajouté avec succès")
                else:
                    print(f"   ❌ Échec ajout")

                # Nettoyage
                os.unlink(temp_file)

            except Exception as e:
                print(f"   ❌ Erreur: {e}")

        # Statistiques finales
        stats = generator.get_statistics()
        print(f"\n📊 STATISTIQUES FINALES:")
        print(f"   • Total documents: {stats['total_documents']}")
        print(f"   • Taille base: {stats['system_info']['database_size_mb']:.2f} MB")


if __name__ == "__main__":
    print("🚀 TESTS D'AJOUT DE DOCUMENTS EXPERTS SCR")
    print("=" * 50)

    # Test principal
    test_add_document()

    # Test multiple
    test_multiple_documents()

    print(f"\n🎉 TESTS TERMINÉS!")
    print(f"💡 Maintenant vous pouvez:")
    print(f"   1. Vérifier: python cli.py stats")
    print(f"   2. Générer: python cli.py generate --ai claude-sonnet-4 --level expert --module spread")
    print(f"   3. Consulter: prompt_enrichi_avec_reglement.txt")