"""
pyjoy.parser - Parser for Joy programs.

Converts a token stream into an AST (nested structure of terms).
"""

from __future__ import annotations

from typing import Any, List, Optional, Set, Tuple

from pyjoy.errors import JoySyntaxError, JoySetMemberError
from pyjoy.scanner import Scanner, Token
from pyjoy.types import JoyValue, JoyQuotation


# Sentinel for terms to skip
_SKIP = object()


class Parser:
    """
    Joy parser: converts token stream to AST.

    AST is a JoyQuotation containing:
    - JoyValue literals (integers, floats, strings, etc.)
    - JoyQuotation for [...] blocks
    - Strings for symbols (resolved at runtime)
    """

    def __init__(self) -> None:
        self._tokens: List[Token] = []
        self._pos: int = 0

    def parse(self, source: str) -> JoyQuotation:
        """
        Parse source code into a program.

        Args:
            source: Joy source code

        Returns:
            JoyQuotation representing the program
        """
        scanner = Scanner()
        self._tokens = list(scanner.tokenize(source))
        self._pos = 0

        terms = self._parse_terms(set())
        return JoyQuotation(tuple(terms))

    def _current(self) -> Optional[Token]:
        """Get current token or None if at end."""
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _advance(self) -> Optional[Token]:
        """Consume and return current token."""
        token = self._current()
        self._pos += 1
        return token

    def _parse_terms(self, terminators: Set[str]) -> List[Any]:
        """
        Parse sequence of terms until a terminator token.

        Args:
            terminators: Set of token types that end the sequence

        Returns:
            List of terms
        """
        terms: List[Any] = []

        while True:
            token = self._current()
            if token is None or token.type in terminators:
                break

            term = self._parse_term()
            if term is not _SKIP:
                terms.append(term)

        return terms

    def _parse_term(self) -> Any:
        """
        Parse a single term.

        Returns:
            JoyValue, JoyQuotation, string (symbol), or _SKIP
        """
        token = self._current()
        if token is None:
            return _SKIP

        if token.type == "INTEGER":
            self._advance()
            return JoyValue.integer(token.value)

        elif token.type == "FLOAT":
            self._advance()
            return JoyValue.floating(token.value)

        elif token.type == "STRING":
            self._advance()
            return JoyValue.string(token.value)

        elif token.type == "CHAR":
            self._advance()
            return JoyValue.char(token.value)

        elif token.type == "LBRACKET":
            return self._parse_quotation()

        elif token.type == "LBRACE":
            return self._parse_set()

        elif token.type == "SYMBOL":
            self._advance()
            name = token.value

            # Handle boolean literals
            if name == "true":
                return JoyValue.boolean(True)
            elif name == "false":
                return JoyValue.boolean(False)

            # Return as symbol string (late binding - resolved at runtime)
            return name

        elif token.type in ("SEMICOLON", "PERIOD"):
            # Statement terminators - skip
            self._advance()
            return _SKIP

        elif token.type == "DEFINE":
            # Definition marker - skip for now
            self._advance()
            return _SKIP

        else:
            raise JoySyntaxError(
                f"Unexpected token: {token.type}",
                token.line,
                token.column,
            )

    def _parse_quotation(self) -> JoyQuotation:
        """
        Parse a quotation [...].

        Returns:
            JoyQuotation containing the parsed terms
        """
        start_token = self._advance()  # Consume '['
        assert start_token is not None

        terms = self._parse_terms({"RBRACKET"})

        end_token = self._current()
        if end_token is None or end_token.type != "RBRACKET":
            raise JoySyntaxError(
                "Expected ']'",
                start_token.line,
                start_token.column,
            )
        self._advance()  # Consume ']'

        return JoyQuotation(tuple(terms))

    def _parse_set(self) -> JoyValue:
        """
        Parse a set literal {...}.

        Set members must be integers in the range [0, 63].

        Returns:
            JoyValue of type SET
        """
        start_token = self._advance()  # Consume '{'
        assert start_token is not None

        terms = self._parse_terms({"RBRACE"})

        end_token = self._current()
        if end_token is None or end_token.type != "RBRACE":
            raise JoySyntaxError(
                "Expected '}'",
                start_token.line,
                start_token.column,
            )
        self._advance()  # Consume '}'

        # Convert to set of integers
        members: Set[int] = set()
        for term in terms:
            if isinstance(term, JoyValue) and term.type.name == "INTEGER":
                member = term.value
                if not (0 <= member <= 63):
                    raise JoySetMemberError(member)
                members.add(member)
            else:
                raise JoySyntaxError(
                    "Set members must be integers in range [0, 63]",
                    start_token.line,
                    start_token.column,
                )

        return JoyValue.joy_set(frozenset(members))


def parse(source: str) -> JoyQuotation:
    """
    Parse Joy source code into a program.

    Args:
        source: Joy source code

    Returns:
        JoyQuotation representing the program
    """
    parser = Parser()
    return parser.parse(source)
