from typing import Optional
from .matcher import *


class ParseError(Exception):
    """Custom exception for pattern parsing errors."""
    pass

class PatternParser:
    """
        Parses a regex string into a tree of Matcher objects.
        Supports literals, character classes, anchors, quantifiers, groups, and backreferences.
    """
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.index = 0
        self.next_group_id = 1

    # --------------------------
    # Utility methods
    # --------------------------
    def peek(self) -> Optional[str]:
        """Return the current character without advancing the pointer."""
        return self.pattern[self.index] if self.index < len(self.pattern) else None

    def advance(self) -> Optional[str]:
        """Return the current character and advance the pointer."""
        char = self.peek()
        if char is not None:
            self.index += 1
        return char

    # --------------------------
    # Main parse entry
    # --------------------------
    def parse(self) -> Matcher:
        """Parse the full pattern and return the root Matcher node."""
        expr = self._parse_expression()
        if self.peek() is not None:
            raise ParseError(f"Unexpected character '{self.peek()}' at position {self.index}")
        return expr

    # --------------------------
    # Expression, term, factor
    # --------------------------
    def _parse_expression(self) -> Matcher:
        """
        Parse alternations: parts separated by '|'.
        Example: a|b|c → AlternationMatcher(Literal('a'), AlternationMatcher(Literal('b'), Literal('c')))
        """
        left = self._parse_term()
        while self.peek() == "|":
            self.advance()
            right = self._parse_term()
            left = AlternationMatcher(left, right)
        return left

    def _parse_term(self) -> Matcher:
        """
        Parse a sequence of factors (concatenation).
        Example: abc → SequenceMatcher(Literal('a'), Literal('b'), Literal('c'))
        """
        factors = []
        while (c := self.peek()) is not None and c not in [")", "|"]:
            factors.append(self._parse_factor())
        if not factors:
            raise ParseError(f"Expected term at position {self.index}")
        # If only one factor, no need for a sequence node
        return factors[0] if len(factors) == 1 else SequenceMatcher(factors)

    def _parse_factor(self) -> Matcher:
        """
        Parse a single factor, optionally followed by a quantifier:
        ?, +, *, {n}, {n,}, {n,m}
        """
        atom = self._parse_atom()   # parse the "base" unit
        nxt = self.peek()

        # Handle simple quantifiers
        if nxt in ["?", "+", "*"]:
            self.advance()
            if nxt == "?": return OptionalMatcher(atom)
            if nxt == "+": return PlusMatcher(atom)
            if nxt == "*": return StarMatcher(atom)

        # Parse {n}, {n,}, {n,m}
        if nxt == "{":
            self.advance()
            content = ""
            while (c := self.peek()) and (c.isdigit() or c == ","):
                content += self.advance()
            if self.advance() != "}":
                raise ParseError(f"Expected closing '}}' for quantifier at position {self.index}")
            return Quantified(atom, "{" + content + "}")

        return atom


    # --------------------------
    # Atom parsing
    # --------------------------
    def _parse_atom(self) -> Matcher:
        """
        Parse the smallest unit of the regex:
        - anchors (^, $)
        - dot (.)
        - escaped sequences (\d, \w, \1)
        - character classes ([...])
        - capture groups (...)
        - literal characters
        """
        c = self.peek()
        if c is None: raise ParseError("Unexpected end of pattern")

        if c == "^": self.advance(); return AnchorStartMatcher()
        if c == "$": self.advance(); return AnchorEndMatcher()
        if c == ".": self.advance(); return AnyMatcher()
        if c == "\\": return self._parse_escape_or_backref()
        if c == "[": return self._parse_charset()
        if c == "(": return self._parse_group()

        # Any other literal character
        return LiteralMatcher(self.advance())

    # --------------------------
    # Specialized atom parsing
    # --------------------------
    def _parse_escape_or_backref(self) -> Matcher:
        """
        Handle escaped sequences:
        - \d → DigitMatcher
        - \w → WordMatcher
        - \1, \2, ... → BackreferenceMatcher
        - other → Literal
        """
        self.advance()  # skip '\'
        ch = self.advance()
        if ch is None: raise ParseError("Dangling backslash at end of pattern")
        if ch.isdigit(): return BackreferenceMatcher(int(ch))
        if ch == "d": return DigitMatcher()
        if ch == "w": return WordMatcher()
        return LiteralMatcher(ch)

    def _parse_charset(self) -> Matcher:
        """
        Parse a character class: [abc], [^abc]
        """
        self.advance()  # skip '['
        negated = False
        if self.peek() == "^":
            negated = True
            self.advance()
        chars = []
        while (c := self.peek()) is not None and c != "]":
            chars.append(self.advance())
        if self.advance() != "]":
            raise ParseError(f"Unterminated character class starting at position {self.index}")
        return CharClassMatcher(chars, negated)

    def _parse_group(self) -> Matcher:
        """
        Parse a capture group: (...).
        Assign a unique group ID for backreferences.
        """
        self.advance()  # skip '('
        group_id = self.next_group_id
        self.next_group_id += 1
        expr = self._parse_expression()
        if self.advance() != ")":
            raise ParseError(f"Unclosed group starting at position {self.index}")
        return CaptureGroupMatcher(expr, group_id)