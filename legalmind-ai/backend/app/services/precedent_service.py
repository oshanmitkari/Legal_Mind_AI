"""
F11: Legal Precedent & Case Similarity Engine
FAISS-based vector similarity search for historical precedents
"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from app.models import HistoricalCase, Case
from flask import current_app


class PrecedentSearchService:
    """Service for finding similar historical legal precedents using FAISS"""
    
    def __init__(self):
        self.model_name = 'all-MiniLM-L6-v2'  # Lightweight but effective embedding model
        self.model = None
        self.index = None
        self.historical_cases = []
        
    def initialize_model(self):
        """Initialize the sentence transformer model"""
        if self.model is None:
            print(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("✓ Model loaded successfully")
    
    def build_index(self, historical_cases):
        """Build FAISS index from historical cases
        
        Args:
            historical_cases: List of HistoricalCase objects
        """
        self.initialize_model()
        
        if not historical_cases:
            raise ValueError("No historical cases provided for indexing")
        
        self.historical_cases = historical_cases
        
        # Create embeddings for case descriptions
        print(f"Creating embeddings for {len(historical_cases)} historical cases...")
        descriptions = [case.description for case in historical_cases]
        embeddings = self.model.encode(descriptions, show_progress_bar=True)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
        self.index.add(embeddings.astype('float32'))
        
        print(f"✓ FAISS index built with {self.index.ntotal} cases")
    
    def find_similar_cases(self, query_description, top_k=3):
        """Find top-k most similar historical cases
        
        Args:
            query_description: Current case description to match against
            top_k: Number of similar cases to return (default: 3)
            
        Returns:
            List of tuples: [(HistoricalCase, similarity_score), ...]
        """
        if self.index is None or self.model is None:
            raise RuntimeError("Index not built. Call build_index() first.")
        
        # Create embedding for query
        query_embedding = self.model.encode([query_description])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search FAISS index
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Return matched cases with scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.historical_cases):
                case = self.historical_cases[idx]
                case.relevance_score = float(score) * 100  # Convert to percentage
                results.append((case, float(score) * 100))
        
        return results


# Global service instance
precedent_service = PrecedentSearchService()


def get_precedent_service():
    """Get or initialize the precedent search service"""
    global precedent_service
    
    # Build index if not already built
    if precedent_service.index is None:
        historical_cases = HistoricalCase.query.all()
        if historical_cases:
            precedent_service.build_index(historical_cases)
        else:
            print("⚠️  No historical cases found in database. Run seed_historical_cases.py first.")
    
    return precedent_service


def find_similar_precedents(case_id, top_k=3):
    """Find similar historical precedents for a given case
    
    Args:
        case_id: ID of the current case
        top_k: Number of precedents to return
        
    Returns:
        List of tuples: [(HistoricalCase, similarity_score), ...]
    """
    # Get current case
    case = Case.query.get(case_id)
    if not case:
        raise ValueError(f"Case {case_id} not found")
    
    # Get search service
    service = get_precedent_service()
    
    # Build query from case description and type
    query_text = f"{case.description}\nCase Type: {case.case_type}"
    
    # Find similar cases
    similar_cases = service.find_similar_cases(query_text, top_k=top_k)
    
    return similar_cases
