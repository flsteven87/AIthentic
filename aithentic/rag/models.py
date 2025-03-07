from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import uuid

@dataclass
class Document:
    """Represents a document with its metadata."""
    
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Chunk:
    """Represents a chunk of a document."""
    
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: str = None
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
