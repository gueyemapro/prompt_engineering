# ==========================================
# 2. TEST AVEC DOCUMENT RÉEL
# Fichier: test_with_document.py
# ==========================================

def test_with_real_document():
    """Test avec ajout d'un document HTML réaliste"""
    print("📄 TEST AVEC DOCUMENT RÉEL")
    print("=" * 40)

    import tempfile
    import os
    from pathlib import Path

    # Création d'un document HTML réaliste
    realistic_html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>SCR de spread - Guide technique Solvabilité 2</title>
        <meta name="description" content="Calcul du SCR de spread selon le Règlement délégué">
    </head>
    <body>
        <h1>Calcul du SCR de spread selon l'Article 180</h1>

        <h2>1. Principe général</h2>
        <p>Le SCR de spread couvre le risque de perte résultant de la variation des spreads de crédit 
        par rapport à la courbe des taux sans risque selon l'Article 180 du Règlement délégué (UE) 2015/35.</p>

        <h2>2. Formule de calcul</h2>
        <p>SCR_spread = SCR_bonds + SCR_securitisation + SCR_cd</p>

        <h3>2.1 Calcul SCR_bonds</h3>
        <p>Pour chaque obligation i : SCR_bonds_i = Duration_i × Facteur_stress_i × Exposition_i</p>

        <h2>3. Facteurs de stress par notation</h2>
        <table>
            <tr><th>Notation</th><th>Duration 1 an</th><th>Duration 5 ans</th><th>Duration 10 ans</th></tr>
            <tr><td>AAA</td><td>0.9%</td><td>4.5%</td><td>9.0%</td></tr>
            <tr><td>AA</td><td>1.1%</td><td>5.5%</td><td>11.0%</td></tr>
            <tr><td>A</td><td>1.4%</td><td>7.0%</td><td>14.0%</td></tr>
            <tr><td>BBB</td><td>2.5%</td><td>12.5%</td><td>25.0%</td></tr>
            <tr><td>BB</td><td>4.5%</td><td>22.5%</td><td>45.0%</td></tr>
            <tr><td>B ou moins</td><td>7.5%</td><td>37.5%</td><td>75.0%</td></tr>
            <tr><td>Non noté</td><td>3.0%</td><td>15.0%</td><td>30.0%</td></tr>
        </table>

        <h2>4. Règles spéciales</h2>
        <h3>4.1 Duration minimale (Article 181)</h3>
        <p>La duration modifiée ne peut jamais être inférieure à 1 an.</p>

        <h3>4.2 Obligations souveraines</h3>
        <p>Les obligations d'États membres de l'UE en devise locale sont exemptées du choc spread.</p>

        <h3>4.3 Plafonnement</h3>
        <p>Le choc de spread ne peut excéder 100% de la valeur de l'obligation.</p>

        <h2>5. Exemple de calcul</h2>
        <div class="example">
            <h4>Obligation corporate BBB de 100M€, duration 8 ans</h4>
            <p>Facteur de stress interpolé : 8 × 2.5% = 20%</p>
            <p>SCR = 100M€ × 20% = 20M€</p>
        </div>

        <h2>6. Corrélations</h2>
        <p>Le SCR spread est corrélé avec les autres sous-modules selon la matrice de corrélation 
        de l'Annexe IV. Notamment, corrélation de 50% avec le module taux (révision 2025 : 25%).</p>

        <footer>
            <p>Source : Règlement délégué (UE) 2015/35, Articles 175-181</p>
            <p>Dernière mise à jour : Guidelines EIOPA 2023</p>
        </footer>
    </body>
    </html>
    """

    try:
        # Sauvegarde du document temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(realistic_html)
            temp_file = f.name

        print(f"📝 Document créé: {Path(temp_file).name}")

        # Initialisation du générateur
        from src.main import SCRPromptGenerator
        from src.knowledge.models import PromptConfig
        from src.config import AIProvider, ExpertiseLevel, SCRModule, DocumentType

        generator = SCRPromptGenerator()

        # Ajout du document
        print("\n📤 Ajout du document...")
        success = generator.add_document_source(
            file_path_or_url=temp_file,
            doc_type=DocumentType.EIOPA_GUIDELINES,
            scr_modules=[SCRModule.SPREAD],
            title="Guide SCR Spread - Test",
            reliability_score=0.9
        )

        if success:
            print("✅ Document ajouté avec succès")
        else:
            print("❌ Échec ajout document")
            return False

        # Vérification en base
        print("\n🔍 Vérification en base...")
        docs = generator.knowledge_base.get_documents_by_module(SCRModule.SPREAD)
        print(f"✅ Documents spread trouvés: {len(docs)}")

        if docs:
            doc = docs[0]
            print(f"   Titre: {doc.title}")
            print(f"   Articles extraits: {doc.regulatory_articles}")
            print(f"   Score fiabilité: {doc.reliability_score}")

        # Génération de prompt enrichi
        print("\n🤖 Génération de prompt enrichi...")
        config = PromptConfig(
            ai_provider=AIProvider.CLAUDE_SONNET_4,
            expertise_level=ExpertiseLevel.EXPERT,
            scr_module=SCRModule.SPREAD,
            max_length=4000
        )

        result = generator.generate_optimized_prompt(config)

        print(f"✅ Prompt généré: {len(result['prompt'])} caractères")
        print(f"✅ Sources utilisées: {result['metadata']['knowledge_base_stats']['relevant_documents']}")

        # Affichage d'un extrait
        print(f"\n📄 EXTRAIT DU PROMPT GÉNÉRÉ:")
        print("-" * 50)
        extract = result['prompt'][:400] + "..." if len(result['prompt']) > 400 else result['prompt']
        print(extract)
        print("-" * 50)

        # Vérifications de qualité
        print(f"\n✅ VÉRIFICATIONS DE QUALITÉ:")
        checks = [
            ("Mention Article 180", "180" in result['prompt']),
            ("Mention facteurs de stress",
             "facteur" in result['prompt'].lower() and "stress" in result['prompt'].lower()),
            ("Mention duration", "duration" in result['prompt'].lower()),
            ("Mention BBB", "BBB" in result['prompt']),
            ("Structure professionnelle", "SYNTHÈSE" in result['prompt'] or "synthèse" in result['prompt']),
        ]

        for check_name, passed in checks:
            status = "✅" if passed else "⚠️"
            print(f"   {status} {check_name}")

        generator.close()
        print(f"\n🎉 TEST AVEC DOCUMENT RÉUSSI!")
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False
    finally:
        # Nettoyage
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)