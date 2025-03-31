import re
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Handle common Unicode characters
    text = text.replace('\u2019', "'")  # Right single quotation mark
    text = text.replace('\u2018', "'")  # Left single quotation mark
    text = text.replace('\u201c', '"')  # Left double quotation mark
    text = text.replace('\u201d', '"')  # Right double quotation mark
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '--')  # Em dash
    
    return text

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex."""
    # Simple regex-based sentence splitter
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    return [s.strip() for s in sentences if s.strip()]

def normalize_line_breaks(text: str) -> str:
    """Normalize different line break styles."""
    # Replace all types of line breaks with standard newlines
    text = re.sub(r'\r\n|\r|\n', '\n', text)
    
    # Remove more than 2 consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text