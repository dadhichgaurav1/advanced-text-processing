"""Synonym provider using spacy-wordnet and NLTK WordNet."""

from typing import List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class SynonymProvider:
    """Provides synonyms using spacy-wordnet and NLTK WordNet fallback."""
    
    def __init__(
        self,
        use_spacy_wordnet: bool = True,
        use_nltk_fallback: bool = True,
        filter_by_pos: bool = True
    ):
        """
        Initialize synonym provider.
        
        Args:
            use_spacy_wordnet: Use spacy-wordnet for synonyms
            use_nltk_fallback: Use NLTK WordNet as fallback
            filter_by_pos: Filter synonyms by part-of-speech
        """
        self.use_spacy_wordnet = use_spacy_wordnet
        self.use_nltk_fallback = use_nltk_fallback
        self.filter_by_pos = filter_by_pos
        
        # Initialize spacy-wordnet if available
        self.spacy_wordnet_available = False
        if use_spacy_wordnet:
            try:
                # First ensure NLTK WordNet is available (spacy-wordnet depends on it)
                import nltk
                from nltk.corpus import wordnet
                try:
                    wordnet.synsets("test")
                except LookupError:
                    logger.info("Downloading WordNet for spacy-wordnet...")
                    nltk.download('wordnet', quiet=True)
                    nltk.download('omw-1.4', quiet=True)
                
                # Now try to import spacy-wordnet
                from spacy_wordnet.wordnet_annotator import WordnetAnnotator
                self.spacy_wordnet_available = True
                logger.info("spacy-wordnet initialized successfully")
            except ImportError as e:
                logger.warning(f"spacy-wordnet not available: {e}. Install with: pip install spacy-wordnet")
            except Exception as e:
                logger.warning(f"spacy-wordnet initialization failed: {e}")
        
        # Initialize NLTK WordNet if available
        self.nltk_available = False
        if use_nltk_fallback:
            try:
                import nltk
                from nltk.corpus import wordnet as wn
                
                # Try to access wordnet, download if needed
                try:
                    wn.synsets("test")
                    self.nltk_available = True
                    logger.info("NLTK WordNet initialized successfully")
                except LookupError:
                    logger.info("Downloading NLTK WordNet data...")
                    try:
                        nltk.download('wordnet', quiet=True)
                        nltk.download('omw-1.4', quiet=True)
                        # Verify it works after download
                        wn.synsets("test")
                        self.nltk_available = True
                        logger.info("NLTK WordNet downloaded and initialized")
                    except Exception as download_error:
                        logger.warning(f"Failed to download NLTK data: {download_error}")
            except ImportError as import_error:
                logger.warning(f"NLTK not available: {import_error}. Install with: pip install nltk")
            except Exception as e:
                logger.warning(f"NLTK WordNet not available: {e}")
    
    def get_synonyms(
        self,
        word: str,
        pos_tag: Optional[str] = None,
        max_synonyms: int = 5
    ) -> List[str]:
        """
        Get synonyms for a word.
        
        Args:
            word: Word to find synonyms for
            pos_tag: Part-of-speech tag for filtering ('VERB', 'ADJ', 'NOUN', 'ADV')
            max_synonyms: Maximum number of synonyms to return
        
        Returns:
            List of synonym strings
        """
        synonyms = set()
        
        # Try spacy-wordnet first
        if self.spacy_wordnet_available and self.use_spacy_wordnet:
            try:
                syns = self._get_spacy_synonyms(word, pos_tag)
                synonyms.update(syns)
            except Exception as e:
                logger.debug(f"spacy-wordnet error for '{word}': {e}")
        
        # Use NLTK fallback if needed
        if self.nltk_available and self.use_nltk_fallback:
            if not synonyms or len(synonyms) < max_synonyms:
                try:
                    syns = self._get_nltk_synonyms(word, pos_tag)
                    synonyms.update(syns)
                except Exception as e:
                    logger.debug(f"NLTK WordNet error for '{word}': {e}")
        
        # Remove the original word from synonyms
        synonyms.discard(word.lower())
        
        # Convert to list and limit
        synonym_list = list(synonyms)[:max_synonyms]
        
        return synonym_list
    
    def _get_spacy_synonyms(
        self,
        word: str,
        pos_tag: Optional[str] = None
    ) -> Set[str]:
        """Get synonyms using spacy-wordnet."""
        from ner_lib.utils.nlp import get_spacy_model
        
        # Load shared spacy model
        nlp = get_spacy_model()
        
        # Add WordNet component if not already present
        if 'wordnet' not in nlp.pipe_names and 'spacy_wordnet' not in nlp.pipe_names:
            try:
                from spacy_wordnet.wordnet_annotator import WordnetAnnotator
                # Initialize WordNet annotator without config (it auto-detects language)
                nlp.add_pipe("spacy_wordnet", after='tagger')
            except Exception as e:
                logger.warning(f"Could not add wordnet to pipeline: {e}")
                return set()
        
        # Process word (replace underscores with spaces for spaCy processing)
        doc = nlp(word.replace("_", " "))
        
        synonyms = set()
        for token in doc:
            # Access wordnet synsets through token extension
            if hasattr(token._, 'wordnet') and hasattr(token._.wordnet, 'synsets'):
                for synset in token._.wordnet.synsets():
                    for lemma in synset.lemmas():
                        syn_word = lemma.name().replace('_', ' ')
                        # Filter by POS if specified
                        if pos_tag and self.filter_by_pos:
                            if self._match_pos(synset.pos(), pos_tag):
                                synonyms.add(syn_word.lower())
                        else:
                            synonyms.add(syn_word.lower())
        
        return synonyms
    
    def _get_nltk_synonyms(
        self,
        word: str,
        pos_tag: Optional[str] = None
    ) -> Set[str]:
        """Get synonyms using NLTK WordNet."""
        from nltk.corpus import wordnet as wn
        
        # Convert POS tag to WordNet POS
        wordnet_pos = self._convert_pos_to_wordnet(pos_tag) if pos_tag else None
        
        synonyms = set()
        
        # Try with underscores (for multi-word expressions like "rely_on")
        word_underscore = word.replace(" ", "_")
        
        # Get synsets
        if wordnet_pos:
            synsets = wn.synsets(word_underscore, pos=wordnet_pos)
        else:
            synsets = wn.synsets(word_underscore)
        
        for synset in synsets:
            for lemma in synset.lemmas():
                syn_word = lemma.name().replace('_', ' ')
                synonyms.add(syn_word.lower())
        
        return synonyms
    
    def _convert_pos_to_wordnet(self, pos_tag: str) -> Optional[str]:
        """Convert spaCy POS tag to WordNet POS."""
        from nltk.corpus import wordnet as wn
        
        pos_map = {
            'VERB': wn.VERB,
            'NOUN': wn.NOUN,
            'ADJ': wn.ADJ,
            'ADV': wn.ADV
        }
        
        return pos_map.get(pos_tag.upper())
    
    def _match_pos(self, wordnet_pos: str, spacy_pos: str) -> bool:
        """Check if WordNet POS matches spaCy POS tag."""
        pos_map = {
            'v': 'VERB',
            'n': 'NOUN',
            'a': 'ADJ',
            's': 'ADJ',  # Satellite adjective
            'r': 'ADV'
        }
        
        return pos_map.get(wordnet_pos, '').upper() == spacy_pos.upper()
