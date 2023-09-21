import re

class EntityIdentifierDetector:
    """A class to detect the type of a given identifier using predefined patterns."""

    def __init__(self):
        self.identifier_patterns = {
            'doi': re.compile(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', re.I),
            'openalex': re.compile(r'^[A-Z]\d+$'),
            'wikidata': re.compile(r'^Q\d+$'),
            'issn': re.compile(r'^\d{4}-\d{4}$'),
            'ror': re.compile(r'^[a-zA-Z0-9]{9}$')
        }

    def identify(self, identifier: str) -> str:
        """Identify the type of the provided identifier."""
        
        for identifier_type, pattern in self.identifier_patterns.items():
            if pattern.match(identifier):
                return identifier_type
        return None
