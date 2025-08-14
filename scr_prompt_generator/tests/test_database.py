# ==========================================
# SCRIPT DE TEST POUR L'ÉTAPE 3
# Fichier: test_database.py (à la racine)
# ==========================================

def test_database():
    """Test basique de la base de données"""
    import os
    from src.knowledge.database import SCRKnowledgeBase
    from src.knowledge.models import DocumentSource, SCRConcept
    from src.config import DocumentType, SCRModule
    from datetime import date

    print("🧪 TEST DE LA BASE DE DONNÉES")
    print("=" * 40)

    # Nettoyage du fichier de test s'il existe
    test_db = "./test_scr.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    try:
        # Initialisation
        with SCRKnowledgeBase(test_db) as kb:
            print("✅ Base de données initialisée")

            # Test ajout document
            doc = DocumentSource(
                id="test_doc_001",
                title="Document de Test SCR Spread",
                doc_type=DocumentType.REGULATION_EU,
                url="https://example.com/doc.pdf",
                publication_date=date(2023, 1, 15),
                regulatory_articles=["180", "181", "182"],
                scr_modules=[SCRModule.SPREAD, SCRModule.CONCENTRATION],
                reliability_score=0.9,
                content_hash="abc123"
            )

            success = kb.add_document(doc)
            print(f"✅ Document ajouté: {success}")

            # Test récupération
            retrieved_doc = kb.get_document_by_id("test_doc_001")
            print(f"✅ Document récupéré: {retrieved_doc.title if retrieved_doc else 'Non trouvé'}")

            # Test recherche par module
            spread_docs = kb.get_documents_by_module(SCRModule.SPREAD)
            print(f"✅ Documents spread trouvés: {len(spread_docs)}")

            # Test ajout concept
            concept = SCRConcept(
                concept_name="Facteur de stress spread",
                scr_module=SCRModule.SPREAD,
                definition="Facteur appliqué selon la notation et la duration",
                formula="Stress_i = Duration_i × Facteur_notation_i",
                regulatory_article="180",
                examples=["BBB 5 ans: 8.5%", "AAA 10 ans: 4.2%"]
            )

            concept_id = kb.add_scr_concept(concept)
            print(f"✅ Concept ajouté avec ID: {concept_id}")

            # Test statistiques
            stats = kb.get_statistics()
            print(f"✅ Statistiques: {stats['total_documents']} documents")

            print("\n🎉 TOUS LES TESTS PASSÉS!")

    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

    finally:
        # Nettoyage
        if os.path.exists(test_db):
            os.remove(test_db)
            print("🧹 Fichier de test nettoyé")

    return True


if __name__ == "__main__":
    test_database()