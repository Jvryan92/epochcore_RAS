"""Game Terms Integration Example"""

from game_terms import GameTerm, GameVocabulary, TermCategory

# Create vocabulary manager
vocab = GameVocabulary()

# Register some core terms
vocab.register_term(
    GameTerm(
        term="OP",
        category=TermCategory.MECHANICS,
        definition="Overpowered; describes anything considered excessively strong",
        usage="Used to describe unbalanced game elements",
        examples=[
            "That new hero is completely OP",
            "They need to nerf that OP weapon",
            "The current meta is too OP"
        ],
        related_terms=["nerf", "meta", "balance"],
        variants=["overpowered", "overtuned"],
        community_context="Often leads to balance discussions"
    )
)

vocab.register_term(
    GameTerm(
        term="meta",
        category=TermCategory.STRATEGY,
        definition="Most Effective Tactics Available; current optimal strategies",
        usage="Discussing optimal gameplay approaches",
        examples=[
            "The tank meta is back",
            "This build is currently meta",
            "Off-meta picks can still work"
        ],
        related_terms=["tier list", "patch", "balance"],
        variants=["metagame", "meta-strategy"],
        community_context="Changes with patches and discoveries"
    )
)

vocab.register_term(
    GameTerm(
        term="snowball",
        category=TermCategory.MECHANICS,
        definition="Using early advantage to build increasingly larger leads",
        usage="Describing momentum-based gameplay",
        examples=[
            "Their early lead snowballed out of control",
            "This champion snowballs hard",
            "Need to prevent them from snowballing"
        ],
        related_terms=["momentum", "advantage", "comeback"],
        variants=["snowballing", "snowballed"],
        community_context="Important concept in competitive games"
    )
)

# Export to JSON
vocab.export_to_json('data/game_vocabulary.json')

# Example usage
term = vocab.get_term("OP")
print(f"Term: {term.term}")
print(f"Definition: {term.definition}")
print(f"Examples: {term.examples[0]}")

related = vocab.find_related_terms("meta")
print(f"Terms related to meta: {[t.term for t in related]}")

mechanics_terms = vocab.get_terms_by_category(TermCategory.MECHANICS)
print(f"Mechanics terms: {[t.term for t in mechanics_terms]}")
