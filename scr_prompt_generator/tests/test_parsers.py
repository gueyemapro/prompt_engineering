# ==========================================
# SCRIPT DE TEST POUR L'ÉTAPE 4
# Fichier: test_parsers.py (à la racine)
# ==========================================

def test_parsers():
    """Test des parsers de documents"""
    import os
    import tempfile
    from src.parsers import PDFParser, HTMLParser, create_parser

    print("🧪 TEST DES PARSERS DE DOCUMENTS")
    print("=" * 45)

    # Test HTML Parser avec contenu de test
    print("\n1. Test HTML Parser")
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Document Test SCR</title>
        <meta name="description" content="Test document pour SCR">
    </head>
    <body>
        <h1>SCR de Spread</h1>
        <p>Le SCR de spread selon l'Article 180 du Règlement délégué.</p>
        <h2>Formule de calcul</h2>
        <p>SCR_spread = Duration × Facteur de stress</p>
        <table>
            <tr><th>Notation</th><th>Facteur</th></tr>
            <tr><td>AAA</td><td>0.9%</td></tr>
            <tr><td>BBB</td><td>2.5%</td></tr>
        </table>
        <a href="https://eiopa.europa.eu">EIOPA</a>
    </body>
    </html>
    """

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html = f.name

        html_parser = HTMLParser()
        result = html_parser.extract_content(temp_html)

        print(f"✅ HTML - Titre: {result['metadata']['title']}")
        print(f"✅ HTML - Mots: {result['statistics']['word_count']}")
        print(f"✅ HTML - Tableaux: {result['statistics']['table_count']}")

        # Test extraction articles
        articles = html_parser.extract_regulatory_articles(result['text_content'])
        print(f"✅ HTML - Articles trouvés: {articles}")

        # Test mots-clés SCR
        keywords = html_parser.extract_scr_keywords(result['text_content'])
        print(f"✅ HTML - Mots-clés SCR: {keywords[:5]}")

    except Exception as e:
        print(f"❌ Erreur HTML Parser: {e}")
    finally:
        if 'temp_html' in locals():
            os.unlink(temp_html)

    # Test factory
    print(f"\n2. Test Factory")
    try:
        parser = create_parser("test.pdf")
        print(f"✅ Factory PDF: {type(parser).__name__}")

        parser = create_parser("https://example.com")
        print(f"✅ Factory URL: {type(parser).__name__}")

        parser = create_parser("test.html")
        print(f"✅ Factory HTML: {type(parser).__name__}")

    except Exception as e:
        print(f"❌ Erreur Factory: {e}")

    # Test avec URL réelle (optionnel)
    print(f"\n3. Test URL réelle (optionnel)")
    test_url = input("URL à tester (Entrée pour passer): ").strip()

    if test_url:
        try:
            html_parser = HTMLParser()
            result = html_parser.extract_content(test_url)
            print(f"✅ URL - Titre: {result['metadata']['title'][:50]}")
            print(f"✅ URL - Mots: {result['statistics']['word_count']}")

        except Exception as e:
            print(f"❌ Erreur URL: {e}")

    print(f"\n🎉 TESTS PARSERS TERMINÉS!")
    return True


if __name__ == "__main__":
    test_parsers()