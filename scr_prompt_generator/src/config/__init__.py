#==========================================
# Fichier: src/config/__init__.py
# ==========================================

"""
Configuration package for SCR Prompt Generator
"""
from .settings import (
    Config,
    AIProvider,
    ExpertiseLevel,
    SCRModule,
    DocumentType
)

__all__ = [
    'Config',
    'AIProvider',
    'ExpertiseLevel',
    'SCRModule',
    'DocumentType'
]