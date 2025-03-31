import logging
from typing import List, Dict, Any, Optional, Union
from app.core.chroma_client import chroma

def format_filter(filter_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format filter dictionary for ChromaDB query.
    
    Args:
        filter_dict: Dictionary of metadata filters
        
    Returns:
        Formatted filter dictionary compatible with ChromaDB
    """
    if not filter_dict:
        return {}
    
    # ChromaDB supports direct filtering with a dict
    return filter_dict

def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the vector collection.
    
    Returns:
        Dictionary containing collection statistics
    """
    try:
        count = chroma.collection.count()
        return {
            "collection_name": chroma.collection.name,
            "vector_count": count
        }
    except Exception as e:
        logging.error(f"Error getting collection stats: {str(e)}")
        return {
            "collection_name": chroma.collection.name if chroma.collection else "unknown",
            "vector_count": 0,
            "error": str(e)
        }