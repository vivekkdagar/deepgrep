from deepgrep.core.engine import find_matches, match_pattern

def test_literal_match():
    assert match_pattern("hello", "hello") is True
    assert match_pattern("hello", "hell") is True
    assert match_pattern("hello", "world") is False

def test_regex_digits():
    line = "abc 123 def 456"
    pattern = r"\d+"
    matches = find_matches(line, pattern)
    assert matches == ["123", "456"]

def test_regex_word_char():
    line = "hello_world 42"
    pattern = r"\w+"
    matches = find_matches(line, pattern)
    assert matches == ["hello_world", "42"]