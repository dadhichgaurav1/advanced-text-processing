"""Deterministic matching signals."""

from typing import Dict, List, Optional, Set
import spacy
from spacy.matcher import PhraseMatcher
from flashtext import KeywordProcessor

from ner_lib.models.candidate import Citation
from ner_lib.normalization.text import normalize_entity_name


class ExactMatcher:
    """Exact normalized name matching."""
    
    def __init__(self):
        """Initialize exact matcher."""
        self.entity_map: Dict[str, str] = {}  # normalized_name -> entity_id
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """
        Add an entity to the matcher.
        
        Args:
            entity_id: Entity ID
            canonical_name: Canonical name
            aliases: Optional list of aliases
        """
        # Add canonical name
        normalized = normalize_entity_name(canonical_name)
        self.entity_map[normalized] = entity_id
        
        # Add aliases
        if aliases:
            for alias in aliases:
                normalized_alias = normalize_entity_name(alias)
                self.entity_map[normalized_alias] = entity_id
    
    def match(self, mention: str) -> Optional[tuple[str, Citation]]:
        """
        Check for exact match.
        
        Args:
            mention: Normalized mention text
        
        Returns:
            Tuple of (entity_id, citation) if match found, None otherwise
        """
        normalized = normalize_entity_name(mention)
        
        if normalized in self.entity_map:
            entity_id = self.entity_map[normalized]
            citation = Citation(
                source="Custom",
                method="exact_normalized_match",
                component="deterministic",
                confidence_contribution=1.0
            )
            return entity_id, citation
        
        return None


class PhraseMatcherLookup:
    """spaCy PhraseMatcher for fast multi-alias lookup."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize PhraseMatcher.
        
        Args:
            model_name: spaCy model name
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # Model not found, create blank
            self.nlp = spacy.blank("en")
        
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.entity_map: Dict[str, str] = {}  # pattern_id -> entity_id
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """
        Add entity with aliases to matcher.
        
        Args:
            entity_id: Entity ID
            canonical_name: Canonical name
            aliases: Optional list of aliases
        """
        # Collect all names
        names = [canonical_name]
        if aliases:
            names.extend(aliases)
        
        # Create patterns
        patterns = [self.nlp.make_doc(name) for name in names]
        
        # Add to matcher with entity_id as pattern label
        pattern_id = f"entity_{entity_id}"
        self.matcher.add(pattern_id, patterns)
        self.entity_map[pattern_id] = entity_id
    
    def match(self, mention: str) -> Optional[tuple[str, Citation]]:
        """
        Find exact phrase match.
        
        Args:
            mention: Mention text
        
        Returns:
            Tuple of (entity_id, citation) if match found, None otherwise
        """
        doc = self.nlp(mention)
        matches = self.matcher(doc)
        
        if matches:
            # Return first match (pattern_id, start, end)
            pattern_id = self.nlp.vocab.strings[matches[0][0]]
            entity_id = self.entity_map[pattern_id]
            
            citation = Citation(
                source="spaCy",
                method="PhraseMatcher",
                component="exact_lookup",
                confidence_contribution=1.0
            )
            return entity_id, citation
        
        return None


class FlashTextLookup:
    """FlashText KeywordProcessor for ultra-fast exact matching."""
    
    def __init__(self, case_sensitive: bool = False):
        """
        Initialize FlashText processor.
        
        Args:
            case_sensitive: Whether matching should be case-sensitive
        """
        self.processor = KeywordProcessor(case_sensitive=case_sensitive)
        self.entity_map: Dict[str, str] = {}  # keyword -> entity_id
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """
        Add entity with aliases.
        
        Args:
            entity_id: Entity ID
            canonical_name: Canonical name
            aliases: Optional list of aliases
        """
        # Add canonical name
        self.processor.add_keyword(canonical_name, entity_id)
        self.entity_map[canonical_name] = entity_id
        
        # Add aliases
        if aliases:
            for alias in aliases:
                self.processor.add_keyword(alias, entity_id)
                self.entity_map[alias] = entity_id
    
    def match(self, mention: str) -> Optional[tuple[str, Citation]]:
        """
        Find exact keyword match.
        
        Args:
            mention: Mention text
        
        Returns:
            Tuple of (entity_id, citation) if match found, None otherwise
        """
        keywords_found = self.processor.extract_keywords(mention, span_info=False)
        
        if keywords_found:
            entity_id = keywords_found[0]  # First match
            citation = Citation(
                source="FlashText",
                method="KeywordProcessor",
                component="exact_lookup",
                confidence_contribution=1.0
            )
            return entity_id, citation
        
        return None


class DomainMatcher:
    """Match entities by domain/website/email."""
    
    def __init__(self):
        """Initialize domain matcher."""
        self.domain_map: Dict[str, str] = {}  # domain -> entity_id
        self.email_map: Dict[str, str] = {}  # email -> entity_id
    
    def add_entity(self, entity_id: str, metadata: Dict):
        """
        Add entity with domain metadata.
        
        Args:
            entity_id: Entity ID
            metadata: Entity metadata containing 'domain', 'website', or 'email'
        """
        # Extract domain from various fields
        domain = metadata.get('domain')
        website = metadata.get('website')
        email = metadata.get('email')
        
        if domain:
            self.domain_map[domain.lower()] = entity_id
        
        if website:
            # Extract domain from URL
            domain = self._extract_domain(website)
            if domain:
                self.domain_map[domain] = entity_id
        
        if email:
            # Extract domain from email
            if '@' in email:
                domain = email.split('@')[1].lower()
                self.email_map[domain] = entity_id
    
    def match(self, mention: str, metadata: Dict) -> Optional[tuple[str, Citation]]:
        """
        Match by domain/email.
        
        Args:
            mention: Mention text (not used)
            metadata: Mention metadata with 'domain', 'website', or 'email'
        
        Returns:
            Tuple of (entity_id, citation) if match found, None otherwise
        """
        # Check domain
        domain = metadata.get('domain')
        if domain and domain.lower() in self.domain_map:
            entity_id = self.domain_map[domain.lower()]
            citation = Citation(
                source="Custom",
                method="domain_match",
                component="contextual",
                confidence_contribution=1.0
            )
            return entity_id, citation
        
        # Check email
        email = metadata.get('email')
        if email and '@' in email:
            email_domain = email.split('@')[1].lower()
            if email_domain in self.email_map:
                entity_id = self.email_map[email_domain]
                citation = Citation(
                    source="Custom",
                    method="email_domain_match",
                    component="contextual",
                    confidence_contribution=1.0
                )
                return entity_id, citation
        
        return None
    
    @staticmethod
    def _extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL."""
        import re
        # Simple domain extraction
        match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1).lower()
        return None
