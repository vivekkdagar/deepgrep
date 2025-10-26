import spacy
from nltk.corpus import wordnet
from typing import List, Tuple


def get_antonyms(word: str) -> set:
    antonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            for ant in lemma.antonyms():
                antonyms.add(ant.name())
    return antonyms


class SemanticEngine:
    """Semantic search avoiding antonyms and irrelevant words."""

    def __init__(self, model_name: str = "en_core_web_md"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"SpaCy model '{model_name}' not found. Run: python -m spacy download {model_name}"
            )

    def find_semantic_matches(self, text: str, keyword: str, top_n: int = 10) -> List[Tuple[str, float]]:
        doc = self.nlp(text)
        key_token = self.nlp(keyword)[0]
        antonyms = get_antonyms(keyword.lower())
        results = []

        for token in doc:
            if not token.is_alpha or token.is_stop:
                continue
            # Only match similar POS (adjectives/verbs)
            if token.pos_ != key_token.pos_ and key_token.pos_ in {"ADJ", "VERB"}:
                continue
            if token.text.lower() in antonyms:
                continue  # skip antonyms
            sim = key_token.similarity(token)
            results.append((token.text, sim))

        # Sort descending and keep top N
        results = sorted(results, key=lambda x: x[1], reverse=True)[:top_n]
        # Filter out weak matches
        results = [(w, s) for w, s in results if s > 0.45]
        return results