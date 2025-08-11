# ==========================================
# ÉTAPE 3 : BASE DE DONNÉES SQLITE
# Fichier: src/knowledge/database.py
# ==========================================

import sqlite3
import json
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pathlib import Path

from .models import DocumentSource, SCRConcept
from ..config import Config, DocumentType, SCRModule


class SCRKnowledgeBase:
    """Base de connaissances centralisée pour concepts SCR"""

    def __init__(self, db_path: str = None):
        """
        Initialisation de la base de données

        Args:
            db_path: Chemin vers la base SQLite (optionnel)
        """
        self.db_path = db_path or Config.DEFAULT_DB_PATH
        self.logger = logging.getLogger(__name__)

        # Créer le répertoire si nécessaire
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Connexion à la base
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne

        # Initialisation des tables
        self._initialize_database()

        self.logger.info(f"Base de connaissances initialisée: {self.db_path}")

    def _initialize_database(self):
        """Création des tables si nécessaire"""
        cursor = self.conn.cursor()

        # Table des documents sources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                url TEXT,
                file_path TEXT,
                publication_date DATE,
                regulatory_articles TEXT,  -- JSON list
                scr_modules TEXT,  -- JSON list 
                language TEXT DEFAULT 'fr',
                reliability_score REAL DEFAULT 0.8,
                content_hash TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des concepts SCR
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scr_concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_name TEXT NOT NULL,
                scr_module TEXT NOT NULL,
                definition TEXT,
                formula TEXT,
                regulatory_article TEXT,
                source_document_id TEXT,
                examples TEXT,  -- JSON list
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_document_id) REFERENCES documents (id)
            )
        """)

        # Table des templates de prompts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ai_provider TEXT NOT NULL,
                expertise_level TEXT NOT NULL,
                scr_module TEXT NOT NULL,
                template_content TEXT NOT NULL,
                variables TEXT,  -- JSON list des variables
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index pour améliorer les performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_module 
            ON documents(scr_modules)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_concepts_module 
            ON scr_concepts(scr_module)
        """)

        self.conn.commit()
        self.logger.debug("Tables de base de données créées/vérifiées")

    def add_document(self, doc_source: DocumentSource) -> bool:
        """
        Ajout d'un document à la base

        Args:
            doc_source: DocumentSource à ajouter

        Returns:
            True si succès, False sinon
        """
        try:
            cursor = self.conn.cursor()

            # Sérialisation des listes en JSON
            regulatory_articles_json = json.dumps(doc_source.regulatory_articles)
            scr_modules_json = json.dumps([m.value for m in doc_source.scr_modules])

            # Conversion de la date
            pub_date = doc_source.publication_date.isoformat() if doc_source.publication_date else None

            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, title, doc_type, url, file_path, publication_date, 
                 regulatory_articles, scr_modules, language, reliability_score, 
                 content_hash, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_source.id,
                doc_source.title,
                doc_source.doc_type.value,
                doc_source.url,
                doc_source.file_path,
                pub_date,
                regulatory_articles_json,
                scr_modules_json,
                doc_source.language,
                doc_source.reliability_score,
                doc_source.content_hash,
                doc_source.last_updated.isoformat()
            ))

            self.conn.commit()
            self.logger.info(f"Document ajouté: {doc_source.id}")
            return True

        except Exception as e:
            self.logger.error(f"Erreur ajout document {doc_source.id}: {e}")
            self.conn.rollback()
            return False

    def get_document_by_id(self, doc_id: str) -> Optional[DocumentSource]:
        """
        Récupération d'un document par son ID

        Args:
            doc_id: Identifiant du document

        Returns:
            DocumentSource ou None si non trouvé
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_document_source(row)
        return None

    def get_documents_by_module(self, scr_module: SCRModule, limit: int = None) -> List[DocumentSource]:
        """
        Récupération documents par module SCR

        Args:
            scr_module: Module SCR ciblé
            limit: Limite du nombre de résultats (optionnel)

        Returns:
            Liste des DocumentSource
        """
        cursor = self.conn.cursor()

        query = """
            SELECT * FROM documents 
            WHERE scr_modules LIKE ?
            ORDER BY reliability_score DESC, publication_date DESC
        """

        params = [f'%{scr_module.value}%']

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)

        documents = []
        for row in cursor.fetchall():
            documents.append(self._row_to_document_source(row))

        self.logger.debug(f"Trouvé {len(documents)} documents pour module {scr_module.value}")
        return documents

    def _row_to_document_source(self, row: sqlite3.Row) -> DocumentSource:
        """Conversion d'une ligne DB en DocumentSource"""

        # Désérialisation JSON
        regulatory_articles = json.loads(row['regulatory_articles']) if row['regulatory_articles'] else []
        scr_modules = [SCRModule(m) for m in json.loads(row['scr_modules'])] if row['scr_modules'] else []

        # Conversion de la date
        pub_date = None
        if row['publication_date']:
            try:
                pub_date = datetime.fromisoformat(row['publication_date']).date()
            except:
                pass  # Date invalide, on garde None

        # Conversion last_updated
        last_updated = datetime.now()
        if row['last_updated']:
            try:
                last_updated = datetime.fromisoformat(row['last_updated'])
            except:
                pass

        return DocumentSource(
            id=row['id'],
            title=row['title'],
            doc_type=DocumentType(row['doc_type']),
            url=row['url'],
            file_path=row['file_path'],
            publication_date=pub_date,
            regulatory_articles=regulatory_articles,
            scr_modules=scr_modules,
            language=row['language'],
            reliability_score=row['reliability_score'],
            last_updated=last_updated,
            content_hash=row['content_hash'] or ""
        )

    def add_scr_concept(self, concept: SCRConcept) -> int:
        """
        Ajout d'un concept SCR

        Args:
            concept: SCRConcept à ajouter

        Returns:
            ID du concept créé, ou -1 si erreur
        """
        try:
            cursor = self.conn.cursor()

            examples_json = json.dumps(concept.examples) if concept.examples else None

            cursor.execute("""
                INSERT INTO scr_concepts 
                (concept_name, scr_module, definition, formula, regulatory_article, 
                 source_document_id, examples, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                concept.concept_name,
                concept.scr_module.value,
                concept.definition,
                concept.formula,
                concept.regulatory_article,
                concept.source_document_id,
                examples_json,
                concept.created_at.isoformat()
            ))

            concept_id = cursor.lastrowid
            self.conn.commit()

            self.logger.info(f"Concept ajouté: {concept.concept_name} (ID: {concept_id})")
            return concept_id

        except Exception as e:
            self.logger.error(f"Erreur ajout concept {concept.concept_name}: {e}")
            self.conn.rollback()
            return -1

    def get_concepts_by_module(self, scr_module: SCRModule) -> List[SCRConcept]:
        """Récupération des concepts par module SCR"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM scr_concepts 
            WHERE scr_module = ?
            ORDER BY concept_name
        """, (scr_module.value,))

        concepts = []
        for row in cursor.fetchall():
            concepts.append(self._row_to_scr_concept(row))

        return concepts

    def _row_to_scr_concept(self, row: sqlite3.Row) -> SCRConcept:
        """Conversion d'une ligne DB en SCRConcept"""

        examples = json.loads(row['examples']) if row['examples'] else []

        created_at = datetime.now()
        if row['created_at']:
            try:
                created_at = datetime.fromisoformat(row['created_at'])
            except:
                pass

        return SCRConcept(
            id=row['id'],
            concept_name=row['concept_name'],
            scr_module=SCRModule(row['scr_module']),
            definition=row['definition'],
            formula=row['formula'],
            regulatory_article=row['regulatory_article'],
            source_document_id=row['source_document_id'],
            examples=examples,
            created_at=created_at
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques de la base de connaissances"""
        cursor = self.conn.cursor()

        # Comptage total des documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_docs = cursor.fetchone()[0]

        # Comptage par type de document
        cursor.execute("""
            SELECT doc_type, COUNT(*) 
            FROM documents 
            GROUP BY doc_type
        """)
        doc_types_count = dict(cursor.fetchall())

        # Comptage par module SCR (approximatif)
        cursor.execute("SELECT scr_modules FROM documents")
        module_counts = {}
        for (modules_json,) in cursor.fetchall():
            if modules_json:
                modules = json.loads(modules_json)
                for module in modules:
                    module_counts[module] = module_counts.get(module, 0) + 1

        # Concepts par module
        cursor.execute("""
            SELECT scr_module, COUNT(*) 
            FROM scr_concepts 
            GROUP BY scr_module
        """)
        concepts_count = dict(cursor.fetchall())

        return {
            'total_documents': total_docs,
            'documents_by_type': doc_types_count,
            'documents_by_module': module_counts,
            'concepts_by_module': concepts_count,
            'database_path': self.db_path,
            'last_update': datetime.now().isoformat()
        }

    def close(self):
        """Fermeture de la connexion à la base"""
        if self.conn:
            self.conn.close()
            self.logger.info("Connexion base de données fermée")

    def __enter__(self):
        """Support du context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique"""
        self.close()