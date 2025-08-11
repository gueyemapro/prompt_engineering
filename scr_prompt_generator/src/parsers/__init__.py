# ==========================================
# Fichier: src/parsers/__init__.py
# ==========================================

"""
Document parsers package
"""

from .base_parser import BaseDocumentParser
from .pdf_parser import PDFParser
from .html_parser import HTMLParser

# Factory pour créer le bon parser
def create_parser(file_path_or_url: str) -> BaseDocumentParser:
    """
    Factory pour créer le parser approprié
    
    Args:
        file_path_or_url: Chemin fichier ou URL
        
    Returns:
        Instance du parser approprié
    """
    if file_path_or_url.startswith(('http://', 'https://')):
        return HTMLParser()
    elif file_path_or_url.lower().endswith('.pdf'):
        return PDFParser()
    elif file_path_or_url.lower().endswith(('.html', '.htm')):
        return HTMLParser()
    else:
        raise ValueError(f"Type de fichier non supporté: {file_path_or_url}")

__all__ = [
    'BaseDocumentParser',
    'PDFParser', 
    'HTMLParser',
    'create_parser'
]