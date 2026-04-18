"""
F7: Legal Research Engine - FAISS Index Builder for Indian Law Statutes
Loads IPC, CrPC, CPC, IBC, IT Act into dedicated FAISS index
"""
from __future__ import annotations
import os
import json
from typing import List
from app.utils.vector_store import chunk_text, embed_texts


def build_law_index(law_file_path: str, index_directory: str) -> dict:
    """
    Build FAISS index from Indian law statutes text file
    
    Args:
        law_file_path: Path to indian_law_statutes.txt
        index_directory: Directory to store law_index.faiss
        
    Returns:
        Dictionary with indexing statistics
    """
    # Read the law text file
    with open(law_file_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    # Split by sections (each section is separated by double newline)
    sections = []
    current_section = []
    
    for line in full_text.split('\n'):
        line = line.strip()
        if not line:
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
        else:
            current_section.append(line)
    
    # Add last section
    if current_section:
        sections.append('\n'.join(current_section))
    
    # Chunk each section (some sections might be long)
    all_chunks = []
    chunk_metadata = []
    
    for idx, section in enumerate(sections):
        # Extract section identifier (first line usually)
        first_line = section.split('\n')[0]
        
        # Chunk the section
        section_chunks = chunk_text(section, chunk_size=800, overlap=100)
        
        for chunk_idx, chunk in enumerate(section_chunks):
            all_chunks.append(chunk)
            chunk_metadata.append({
                'section_id': idx,
                'section_title': first_line,
                'chunk_index': chunk_idx,
                'total_chunks': len(section_chunks)
            })
    
    # Generate embeddings
    vectors = embed_texts(all_chunks)
    
    # Load or create FAISS index
    faiss = _get_faiss()
    os.makedirs(index_directory, exist_ok=True)
    
    index_path = os.path.join(index_directory, 'law_index.faiss')
    metadata_path = os.path.join(index_directory, 'law_metadata.json')
    
    # Create new index
    import numpy as np
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to index
    index.add(vectors.astype('float32'))
    
    # Save index
    faiss.write_index(index, index_path)
    
    # Save metadata
    metadata = {
        'total_sections': len(sections),
        'total_chunks': len(all_chunks),
        'dimension': dimension,
        'chunks': chunk_metadata,
        'chunk_texts': all_chunks  # Store full text for retrieval
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return {
        'sections_indexed': len(sections),
        'chunks_created': len(all_chunks),
        'index_path': index_path,
        'metadata_path': metadata_path
    }


def search_law_index(index_directory: str, query: str, top_k: int = 5) -> List[dict]:
    """
    Search the law FAISS index for relevant sections
    
    Args:
        index_directory: Directory containing law_index.faiss
        query: Legal research query
        top_k: Number of results to return
        
    Returns:
        List of matching law sections with metadata
    """
    faiss = _get_faiss()
    
    index_path = os.path.join(index_directory, 'law_index.faiss')
    metadata_path = os.path.join(index_directory, 'law_metadata.json')
    
    # Check if index exists
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        raise FileNotFoundError("Law index not found. Please build it first using build_law_index()")
    
    # Load index and metadata
    index = faiss.read_index(index_path)
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Generate query embedding
    from app.utils.vector_store import embed_texts
    query_vector = embed_texts([query]).astype('float32')
    
    # Search
    distances, indices = index.search(query_vector, top_k)
    
    # Compile results
    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx >= 0 and idx < len(metadata['chunks']):
            chunk_meta = metadata['chunks'][idx]
            chunk_text = metadata['chunk_texts'][idx]
            
            results.append({
                'section_title': chunk_meta['section_title'],
                'text': chunk_text,
                'relevance_score': float(distance),
                'chunk_index': chunk_meta['chunk_index'],
                'total_chunks': chunk_meta['total_chunks']
            })
    
    return results


def _get_faiss():
    """Import FAISS lazily"""
    try:
        import faiss
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FAISS is not installed. Install with: pip install faiss-cpu"
        ) from exc
    return faiss


if __name__ == '__main__':
    # Build index if run directly
    import sys
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(script_dir))
    
    law_file = os.path.join(backend_dir, 'data', 'indian_law_statutes.txt')
    index_dir = os.path.join(backend_dir, 'data', 'law_faiss_index')
    
    print("Building Indian Law FAISS index...")
    print(f"Source: {law_file}")
    print(f"Output: {index_dir}")
    
    stats = build_law_index(law_file, index_dir)
    
    print("\n✅ Index built successfully!")
    print(f"Sections indexed: {stats['sections_indexed']}")
    print(f"Chunks created: {stats['chunks_created']}")
    print(f"Index file: {stats['index_path']}")
    print(f"Metadata file: {stats['metadata_path']}")
