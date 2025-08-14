from src.main import SCRPromptGenerator
from src.config import DocumentType, SCRModule

# Vos vrais documents
documents = [
    {
        'file': 'data/documents/expert_papers/academic_scr_modeling.pdf',
        'type': DocumentType.ACADEMIC_PAPER,
        'modules': [SCRModule.SPREAD, SCRModule.EQUITY],
        'title': 'Academic Research on SCR Modeling',
        'reliability': 0.8
    },
    {
        'file': 'data/documents/regulations/reglement_delegue_2015_35.pdf', 
        'type': DocumentType.REGULATION_EU,
        'modules': [SCRModule.SPREAD, SCRModule.EQUITY, SCRModule.INTEREST_RATE],
        'title': 'Règlement délégué (UE) 2015/35',
        'reliability': 1.0
    }
]

with SCRPromptGenerator() as generator:
    print("📚 AJOUT DE VOS DOCUMENTS EXPERTS")
    print("=" * 40)
    
    for i, doc in enumerate(documents, 1):
        print(f"\n📄 [{i}/{len(documents)}] {doc['title']}")
        
        # Vérifier que le fichier existe
        import os
        if not doc['file'].startswith('http') and not os.path.exists(doc['file']):
            print(f"   ⚠️ Fichier non trouvé: {doc['file']}")
            print(f"   💡 Créez d'abord le répertoire et placez-y vos PDFs")
            continue
        
        try:
            success = generator.add_document_source(
                file_path_or_url=doc['file'],
                doc_type=doc['type'],
                scr_modules=doc['modules'],
                title=doc['title'],
                reliability_score=doc['reliability']
            )
            
            if success:
                print(f"   ✅ Ajouté avec succès!")
            else:
                print(f"   ❌ Échec ajout")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Statistiques finales
    stats = generator.get_statistics()
    print(f"\n📊 RÉSULTAT FINAL:")
    print(f"   • Total documents: {stats['total_documents']}")
    print(f"   • Taille base: {stats['system_info']['database_size_mb']:.2f} MB")
    
    if stats['total_documents'] > 0:
        print(f"\n🎯 PROCHAINES ÉTAPES:")
        print(f"   python cli.py generate --ai claude-sonnet-4 --level expert --module spread")
        print(f"   → Le prompt sera enrichi avec vos documents!")

