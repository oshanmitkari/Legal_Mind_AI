"""
Services package for LegalMind AI
Contains business logic and external integrations
"""
from .precedent_service import PrecedentSearchService, get_precedent_service, find_similar_precedents

__all__ = ['PrecedentSearchService', 'get_precedent_service', 'find_similar_precedents']
