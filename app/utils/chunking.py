from typing import List, Dict, Any
from app.utils.text_processing import clean_text, normalize_line_breaks
import re

def chunk_document(document_id: str, text: str, metadata: Dict[str, Any] = None, 
                 chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split a document into overlapping chunks.
    
    Args:
        document_id: The ID of the document
        text: The text content to chunk
        metadata: Additional metadata to include with each chunk
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of dictionaries containing chunk information
    """
    # Clean and normalize text
    text = clean_text(text)
    text = normalize_line_breaks(text)
    
    # Initialize variables
    chunks = []
    metadata = metadata or {}
    
    # If text is shorter than chunk_size, return as a single chunk
    if len(text) <= chunk_size:
        chunks.append({
            "document_id": document_id,
            "text": text,
            "metadata": metadata
        })
        return chunks
    
    # Split into paragraphs first to respect natural boundaries
    paragraphs = re.split(r'\n{2,}', text)
    
    current_chunk = ""
    current_chunk_size = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        paragraph_len = len(paragraph)
        
        # If adding this paragraph exceeds chunk_size, finalize current chunk
        if current_chunk_size + paragraph_len > chunk_size and current_chunk:
            # Add current chunk to list
            chunks.append({
                "document_id": document_id,
                "text": current_chunk.strip(),
                "metadata": metadata
            })
            
            # Start new chunk with overlap
            overlap_start = max(0, len(current_chunk) - chunk_overlap)
            current_chunk = current_chunk[overlap_start:] + "\n\n" + paragraph
            current_chunk_size = len(current_chunk)
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
            current_chunk_size = len(current_chunk)
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append({
            "document_id": document_id,
            "text": current_chunk.strip(),
            "metadata": metadata
        })
    
    return chunks