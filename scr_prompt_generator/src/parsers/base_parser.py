# ==========================================
# ÉTAPE 4 : PARSERS DE DOCUMENTS
# Fichier: src/parsers/base_parser.py
# ==========================================

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging
import re


class BaseDocumentParser(ABC):
    """Interface abstraite pour tous les parsers de documents"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extraction du contenu d'un document

        Args:
            file_path: Chemin vers le fichier

        Returns:
            Dict contenant le contenu extrait
        """
        pass

    def extract_regulatory_articles(self, content: str) -> List[str]:
        """
        Extraction des références d'articles réglementaires

        Args:
            content: Contenu textuel du document

        Returns:
            Liste des articles trouvés
        """
        # Patterns pour identifier les articles réglementaires
        patterns = [
            r'Article\s+(\d+[a-z]?)\b',  # Article 180, Article 180a
            r'Art\.\s+(\d+[a-z]?)\b',  # Art. 180
            r'Article\s+(\d+[a-z]?)\s*\([^)]+\)',  # Article 180 (bis)
            r'(?:Règlement|Regulation).*?(\d+/\d+)',  # Règlement 2015/35
            r'Directive.*?(\d+/\d+/CE)',  # Directive 2009/138/CE
        ]

        articles = set()  # Pour éviter les doublons

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                article = match.group(1).strip()
                if article and len(article) <= 10:  # Filtrer les matches trop longs
                    articles.add(article)

        # Tri et nettoyage
        sorted_articles = sorted(list(articles), key=lambda x: (len(x), x))
        self.logger.debug(f"Articles extraits: {sorted_articles}")

        return sorted_articles

    def extract_scr_keywords(self, content: str) -> List[str]:
        """
        Extraction des mots-clés SCR du contenu

        Args:
            content: Contenu textuel

        Returns:
            Liste des mots-clés SCR trouvés
        """
        scr_keywords = [
            'SCR', 'spread', 'duration', 'rating', 'notation',
            'facteur de stress', 'stress factor', 'choc',
            'obligation', 'bond', 'crédit', 'credit',
            'contrepartie', 'counterparty', 'concentration',
            'taux', 'interest rate', 'actions', 'equity',
            'devise', 'currency', 'opérationnel', 'operational'
        ]

        found_keywords = []
        content_lower = content.lower()

        for keyword in scr_keywords:
            if keyword.lower() in content_lower:
                found_keywords.append(keyword)

        return found_keywords