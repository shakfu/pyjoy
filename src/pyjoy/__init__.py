"""
pyjoy - An accurate Python implementation of the Joy programming language.

Joy is a functional programming language created by Manfred von Thun.
It is a concatenative, stack-based language where programs are built
by composing functions.
"""

from pyjoy.types import JoyType, JoyValue, JoyQuotation
from pyjoy.stack import JoyStack, ExecutionContext
from pyjoy.scanner import Scanner, Token
from pyjoy.parser import Parser
from pyjoy.evaluator import Evaluator, joy_word
from pyjoy.errors import (
    JoyError,
    JoyStackUnderflow,
    JoyTypeError,
    JoyUndefinedWord,
    JoySyntaxError,
    JoySetMemberError,
)

__version__ = "0.1.0"

__all__ = [
    # Types
    "JoyType",
    "JoyValue",
    "JoyQuotation",
    # Stack
    "JoyStack",
    "ExecutionContext",
    # Scanner
    "Scanner",
    "Token",
    # Parser
    "Parser",
    # Evaluator
    "Evaluator",
    "joy_word",
    # Errors
    "JoyError",
    "JoyStackUnderflow",
    "JoyTypeError",
    "JoyUndefinedWord",
    "JoySyntaxError",
    "JoySetMemberError",
]
