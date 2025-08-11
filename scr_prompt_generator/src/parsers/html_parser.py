# ==========================================
# Fichier: src/parsers/html_parser.py
# ==========================================

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
from .base_parser import BaseDocumentParser
from typing import Dict, Any


class HTMLParser(BaseDocumentParser):
    """Parser pour pages web EIOPA, EUR-Lex"""

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SCR-Prompt-Generator/1.0 (Research Tool)'
        })
        self.timeout = 30

    def extract_content(self, file_path_or_url: str) -> Dict[str, Any]:
        """
        Extraction contenu HTML/web

        Args:
            file_path_or_url: Chemin local ou URL

        Returns:
            Dict contenant le contenu extrait
        """
        if file_path_or_url.startswith(('http://', 'https://')):
            return self._extract_from_url(file_path_or_url)
        else:
            return self._extract_from_file(file_path_or_url)

    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extraction depuis une URL"""
        try:
            self.logger.info(f"Récupération de l'URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Détection de l'encodage
            response.encoding = response.apparent_encoding or 'utf-8'
            html_content = response.text

            # Parsing
            soup = BeautifulSoup(html_content, 'html.parser')

            return self._parse_html_content(soup, url, html_content)

        except Exception as e:
            self.logger.error(f"Erreur récupération URL {url}: {e}")
            raise

    def _extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extraction depuis un fichier local"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Fichier HTML non trouvé: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            return self._parse_html_content(soup, str(file_path), html_content)

        except Exception as e:
            self.logger.error(f"Erreur traitement fichier {file_path}: {e}")
            raise

    def _parse_html_content(self, soup: BeautifulSoup, source: str, raw_html: str) -> Dict[str, Any]:
        """Parsing du contenu HTML"""

        # Nettoyage: suppression des scripts et styles
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Extraction du texte principal
        text_content = soup.get_text(separator='\n', strip=True)

        # Métadonnées
        metadata = {
            'title': soup.title.string.strip() if soup.title else '',
            'description': '',
            'keywords': '',
            'language': soup.get('lang', '')
        }

        # Meta tags
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')

        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '')

        # Extraction des liens
        links = []
        base_url = source if source.startswith('http') else ''

        for link in soup.find_all('a', href=True):
            href = link['href']
            if base_url:
                href = urljoin(base_url, href)

            link_text = link.get_text(strip=True)
            if link_text and len(link_text) > 3:  # Filtrer les liens vides
                links.append({
                    'text': link_text[:100],  # Limitation de taille
                    'url': href
                })

        # Extraction des tableaux
        tables = []
        for i, table in enumerate(soup.find_all('table')):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_data.append(row_data)

            if table_data:
                tables.append({
                    'index': i,
                    'data': table_data
                })

        # Extraction des titres (structure)
        headings = []
        for level in range(1, 7):  # h1 à h6
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    'level': level,
                    'text': heading.get_text(strip=True)
                })

        # Statistiques
        word_count = len(text_content.split()) if text_content else 0

        result = {
            'text_content': text_content,
            'html_content': raw_html,
            'metadata': metadata,
            'links': links[:50],  # Max 50 liens
            'tables': tables,
            'headings': headings,
            'statistics': {
                'word_count': word_count,
                'char_count': len(text_content),
                'link_count': len(links),
                'table_count': len(tables),
                'heading_count': len(headings)
            },
            'source_info': {
                'source': source,
                'type': 'url' if source.startswith('http') else 'file'
            }
        }

        self.logger.info(f"HTML traité: {metadata['title'][:50]} ({word_count} mots)")
        return result