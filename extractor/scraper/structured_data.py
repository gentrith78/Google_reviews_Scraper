from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class WebsiteInstance:
    name: str
    website:str
    contacts:List[str] = field(default_factory=list)

phone_numbers_patterns = [
    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?: ?x\d+)?',
    r'\+1 \(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,10}',
    r'\+\d{1,4}[-.\s]?\d{1,10}',
    r'\b(01\d{4}|\+44 \d{3} \d{4})\b',
    r'\b\(0\d\)\s\d{4}\s\d{4}|\+61\s\d\s\d{4}\s\d{4}\b',
    r'\b0\d{3}\s\d{3}\s\d{4}|\+49\s\d{3}\s\d{3}\s\d{4}\b',
    r'\b0\d{1}\s\d{2}\s\d{2}\s\d{2}\s\d{2}\b',
    r'\b9\d{2}\s\d{3}\s\d{3}|\+34\s\d{3}\s\d{3}\s\d{3}\b',
    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+1\s\d{3}\s\d{3}\s\d{4}',
    r'\d{3,6}(?: {2,3}\d{3,6})+',
    r'\d{3,6} *[ ,;]? *',
    r'\b\d{3} \d{4} \d{4}\b'
]
