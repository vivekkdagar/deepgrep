import pytest
from deepgrep.core.semantic_engine import SemanticEngine

@pytest.fixture
def engine():
    return SemanticEngine()

def test_semantic_similarity(engine):
    text = "I feel happy and joyful"
    keyword = "happy"
    results = engine.find_semantic_matches(text, keyword)
    words = [w for w, _ in results]
    assert "happy" in words or "joyful" in words