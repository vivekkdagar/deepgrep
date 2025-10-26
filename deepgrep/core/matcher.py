from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, Set, List


# --------------------------
# Match State for Backreferences
# --------------------------

@dataclass(frozen=True)
class MatchState:
    """
    Represents the current matching state while processing a line.

    Attributes:
        pos (int): Current position in the string being matched.
        groups (Dict[int, str]): Dictionary storing capture group matches.
    """
    pos: int
    groups: Dict[int, str] = field(compare=False)

    def __hash__(self) -> int:
        """
        Hash method ensures MatchState can be used in sets.
        Groups are sorted to maintain consistency in hashing.
        """
        return hash((self.pos, tuple(sorted(self.groups.items()))))

# --------------------------
# Matchers
# --------------------------
class Matcher:
    """Abstract base class for all matchers."""
    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        """Return a set of next possible MatchStates if this matcher succeeds."""
        raise NotImplementedError("Subclasses must implement match() method.")

class LiteralMatcher(Matcher):
    """Matches a single literal character."""
    def __init__(self, char: str):
        self.char = char

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if state.pos < len(line) and line[state.pos] == self.char:
            # Advance position by 1 if match
            return {MatchState(state.pos + 1, state.groups)}
        return set()  # No match

class DigitMatcher(Matcher):
    """Matches a single digit character."""
    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if state.pos < len(line) and line[state.pos].isdigit():
            return {MatchState(state.pos + 1, state.groups)}
        return set()

class WordMatcher(Matcher):
    """
    Matches a word character: alphanumeric or underscore.
    Equivalent to regex \w.
    """
    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if state.pos < len(line) and (line[state.pos].isalnum() or line[state.pos] == "_"):
            return {MatchState(state.pos + 1, state.groups)}
        return set()


class AnyMatcher(Matcher):
    """Matches any single character except end-of-string."""
    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if state.pos < len(line):
            return {MatchState(state.pos + 1, state.groups)}
        return set()


class CharClassMatcher(Matcher):
    """
    Matches a single character from a set or its negation.

    Args:
        charset: list of allowed characters
        negated: if True, matches any character NOT in charset
    """

    def __init__(self, charset: List[str], negated: bool):
        self.charset = charset
        self.negated = negated

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if state.pos >= len(line):
            return set()
        c = line[state.pos]
        if (not self.negated and c in self.charset) or (self.negated and c not in self.charset):
            return {MatchState(state.pos + 1, state.groups)}
        return set()

class SequenceMatcher(Matcher):
    """Matches a sequence of matchers in order."""
    def __init__(self, matchers: List[Matcher]):
        self.matchers = matchers

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        states = {state}
        for matcher in self.matchers:
            next_states = set()
            for s in states:
                next_states |= matcher.match(line, s)
            states = next_states
            if not states:
                break  # Early exit if no matches remain
        return states

class AlternationMatcher(Matcher):
    """Matches either left or right matcher."""
    def __init__(self, left: Matcher, right: Matcher):
        self.left = left
        self.right = right

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        return self.left.match(line, state) | self.right.match(line, state)


class OptionalMatcher(Matcher):
    """Matches zero or one occurrence of a matcher (like '?')."""
    def __init__(self, matcher: Matcher):
        self.matcher = matcher

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        # Either match nothing or match the node
        return {state} | self.matcher.match(line, state)

class PlusMatcher(Matcher):
    """Matches one or more occurrences of a matcher (like '+')."""
    def __init__(self, matcher: Matcher):
        self.matcher = matcher

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        results = self.matcher.match(line, state)
        all_states = set(results)
        while results:
            next_results = set()
            for s in results:
                next_results |= self.matcher.match(line, s)
            new_states = next_results - all_states
            if not new_states:
                break
            all_states |= new_states
            results = new_states
        return all_states


class StarMatcher(Matcher):
    """Matches zero or more occurrences of a matcher (like '*')."""
    def __init__(self, matcher: Matcher):
        self.matcher = matcher

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        all_states = {state}
        current = {state}
        while current:
            next_states = set()
            for s in current:
                next_states |= self.matcher.match(line, s)
            new_states = next_states - all_states
            if not new_states:
                break
            all_states |= new_states
            current = new_states
        return all_states


# --------------------------
# Anchors
# --------------------------

class AnchorStartMatcher(Matcher):
    """Matches start of string (^)."""
    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        return {state} if state.pos == 0 else set()


class AnchorEndMatcher(Matcher):
    """Matches end of string ($)."""
    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        return {state} if state.pos == len(line) else set()

# --------------------------
# Capture Groups & Backreferences
# --------------------------

class CaptureGroupMatcher(Matcher):
    """Captures matched substring into a group."""
    def __init__(self, matcher: Matcher, gid: int):
        self.matcher = matcher
        self.gid = gid

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        results = self.matcher.match(line, state)
        updated = set()
        for r in results:
            gcopy = deepcopy(r.groups)
            gcopy[self.gid] = line[state.pos:r.pos]
            updated.add(MatchState(r.pos, gcopy))
        return updated


class BackreferenceMatcher(Matcher):
    """Matches the same string as previously captured in a group."""
    def __init__(self, gid: int):
        self.gid = gid

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if self.gid not in state.groups:
            return set()
        ref = state.groups[self.gid]
        if line[state.pos:state.pos + len(ref)] == ref:
            return {MatchState(state.pos + len(ref), state.groups)}
        return set()

# --------------------------
# Quantifiers
# --------------------------

class Quantified(Matcher):
    """
    Wraps a matcher and applies quantifiers: ?, +, *, {n}, {n,}, {n,m}.
    """
    def __init__(self, node: Matcher, kind: str):
        self.node = node
        self.kind = kind

    def match(self, line: str, state: MatchState) -> Set[MatchState]:
        if self.kind == "?":
            return {state} | self.node.match(line, state)
        elif self.kind == "+":
            return PlusMatcher(self.node).match(line, state)
        elif self.kind == "*":
            return StarMatcher(self.node).match(line, state)
        elif self.kind.startswith("{") and self.kind.endswith("}"):
            # parse {n}, {n,}, {n,m}
            content = self.kind[1:-1]
            results = [(state.pos, state.groups)]
            if "," in content:
                # {n,} or {n,m}
                parts = content.split(",")
                n = int(parts[0])
                m = int(parts[1]) if len(parts) > 1 and parts[1] else None
                # Apply minimum n matches
                for _ in range(n):
                    next_results = []
                    for p, g in results:
                        ms = self.node.match(line, MatchState(p, g))
                        for mstate in ms:
                            next_results.append((mstate.pos, mstate.groups))
                    results = next_results
                    if not results:
                        return set()
                # Apply remaining optional matches up to m (or unlimited)
                if m is None:
                    all_states = set(MatchState(p, g) for p, g in results)
                    for p, g in results:
                        all_states |= StarMatcher(self.node).match(line, MatchState(p, g))
                    return all_states
                else:
                    for _ in range(m - n):
                        next_results = []
                        for p, g in results:
                            ms = self.node.match(line, MatchState(p, g))
                            for mstate in ms:
                                next_results.append((mstate.pos, mstate.groups))
                        results += next_results
                    return {MatchState(p, g) for p, g in results}
            else:
                # {n}
                n = int(content)
                for _ in range(n):
                    next_results = []
                    for p, g in results:
                        ms = self.node.match(line, MatchState(p, g))
                        for mstate in ms:
                            next_results.append((mstate.pos, mstate.groups))
                    results = next_results
                    if not results:
                        return set()
                return {MatchState(p, g) for p, g in results}
        else:
            return self.node.match(line, state)






