# engine.py

from .parser import PatternParser
from .matcher import MatchState

from functools import lru_cache
from .parser import PatternParser
from .matcher import MatchState

# core/engine.py
from copy import deepcopy
from functools import lru_cache
from .parser import PatternParser

@lru_cache(maxsize=512)
def compile_pattern(pattern: str):
    """Parse pattern once and cache the result"""
    parser = PatternParser(pattern)
    return parser.parse()

def find_matches(line: str, pattern: str):
    matcher = deepcopy(compile_pattern(pattern))  # <-- deepcopy per use
    matches = []
    i = 0
    L = len(line)

    while i < L:
        initial_state = MatchState(pos=i, groups={})
        next_states = matcher.match(line, initial_state)
        if not next_states:
            i += 1
            continue
        longest_pos = max(state.pos for state in next_states)
        matches.append(line[i:longest_pos])
        i = max(longest_pos, i + 1)
    return matches

def match_pattern(line: str, pattern: str):
    matcher = deepcopy(compile_pattern(pattern))  # <-- deepcopy per use
    start_positions = [0] if pattern.startswith("^") else range(len(line))
    for i in start_positions:
        initial_state = MatchState(pos=i, groups={})
        if matcher.match(line, initial_state):
            return True
    return False