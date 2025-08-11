# ==========================================
# Fichier: src/parsers/pdf_parser.py
# ==========================================

import PyPDF2
import pdfplumber
from pathlib import Path
from .base_parser import BaseDocumentParser
from typing import Dict, Any

class PDFParser(BaseDocumentParser):
    """Parser pour documents PDF (Règlements UE, EIOPA docs)"""

    def __init__(self):
        super().__init__()
        self.max_pages = 200  # Limite pour éviter les docs trop volumineux

    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extraction du contenu PDF avec métadonnées

        Args:
            file_path: Chemin vers le fichier PDF

        Returns:
            Dict contenant le contenu extrait
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Fichier PDF non trouvé: {file_path}")

        if not file_path.suffix.lower() == '.pdf':
            raise ValueError(f"Le fichier n'est pas un PDF: {file_path}")

        try:
            # Extraction avec PyPDF2 pour les métadonnées
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Vérification du nombre de pages
                num_pages = len(pdf_reader.pages)
                if num_pages > self.max_pages:
                    self.logger.warning(f"Document volumineux ({num_pages} pages), traitement partiel")
                    pages_to_process = self.max_pages
                else:
                    pages_to_process = num_pages

                # Métadonnées
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    }

                # Extraction du texte avec PyPDF2
                text_content = ""
                for i in range(pages_to_process):
                    try:
                        page_text = pdf_reader.pages[i].extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    except Exception as e:
                        self.logger.warning(f"Erreur page {i + 1}: {e}")
                        continue

            # Extraction des tableaux avec pdfplumber
            tables = []
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages[:min(10, pages_to_process)]):  # Max 10 pages pour les tableaux
                        page_tables = page.extract_tables()
                        if page_tables:
                            for table in page_tables:
                                if table and len(table) > 1:  # Au moins 2 lignes
                                    tables.append({
                                        'page': i + 1,
                                        'data': table
                                    })
            except Exception as e:
                self.logger.warning(f"Erreur extraction tableaux: {e}")

            # Calcul de statistiques
            word_count = len(text_content.split()) if text_content else 0
            char_count = len(text_content) if text_content else 0

            result = {
                'text_content': text_content,
                'metadata': metadata,
                'tables': tables,
                'statistics': {
                    'page_count': num_pages,
                    'pages_processed': pages_to_process,
                    'word_count': word_count,
                    'char_count': char_count,
                    'table_count': len(tables)
                },
                'file_info': {
                    'name': file_path.name,
                    'size_mb': file_path.stat().st_size / (1024 * 1024),
                    'extension': file_path.suffix
                }
            }

            self.logger.info(f"PDF traité: {file_path.name} ({pages_to_process} pages, {word_count} mots)")
            return result

        except Exception as e:
            self.logger.error(f"Erreur traitement PDF {file_path}: {e}")
            raise