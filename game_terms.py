"""Game Terms Integration System"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TermCategory(Enum):
    """Categories for game terms"""
    MECHANICS = "mechanics"
    COMPETITIVE = "competitive"
    SOCIAL = "social"
    META = "meta"
    TECHNICAL = "technical"
    PROGRESSION = "progression"
    STRATEGY = "strategy"


@dataclass
class GameTerm:
    """Represents a gaming term/slang with context"""
    term: str
    category: TermCategory
    definition: str
    usage: str
    examples: List[str]
    related_terms: List[str]
    variants: List[str]
    community_context: Optional[str] = None


class GameVocabulary:
    """Manages gaming vocabulary and contextual usage"""

    def __init__(self):
        self.terms: Dict[str, GameTerm] = {}
        self.category_index: Dict[TermCategory, List[str]] = {
            cat: [] for cat in TermCategory
        }

    def register_term(self, term: GameTerm) -> None:
        """Register a new gaming term"""
        self.terms[term.term.lower()] = term
        self.category_index[term.category].append(term.term.lower())

    def get_term(self, term: str) -> Optional[GameTerm]:
        """Get details for a specific term"""
        return self.terms.get(term.lower())

    def get_terms_by_category(self, category: TermCategory) -> List[GameTerm]:
        """Get all terms in a category"""
        return [
            self.terms[term]
            for term in self.category_index[category]
        ]

    def find_related_terms(self, term: str) -> List[GameTerm]:
        """Find terms related to the given term"""
        base_term = self.get_term(term)
        if not base_term:
            return []

        related = []
        for related_term in base_term.related_terms:
            if term := self.get_term(related_term):
                related.append(term)

        return related

    def export_to_json(self, filepath: str) -> None:
        """Export vocabulary to JSON"""
        with open(filepath, 'w') as f:
            json.dump(
                {
                    term: {
                        "category": t.category.value,
                        "definition": t.definition,
                        "usage": t.usage,
                        "examples": t.examples,
                        "related_terms": t.related_terms,
                        "variants": t.variants,
                        "community_context": t.community_context
                    }
                    for term, t in self.terms.items()
                },
                f,
                indent=2
            )

    @classmethod
    def from_json(cls, filepath: str) -> 'GameVocabulary':
        """Load vocabulary from JSON"""
        vocab = cls()
        with open(filepath) as f:
            data = json.load(f)
            for term, info in data.items():
                vocab.register_term(
                    GameTerm(
                        term=term,
                        category=TermCategory(info["category"]),
                        definition=info["definition"],
                        usage=info["usage"],
                        examples=info["examples"],
                        related_terms=info["related_terms"],
                        variants=info["variants"],
                        community_context=info["community_context"]
                    )
                )
        return vocab
