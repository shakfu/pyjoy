"""
pyjoy.evaluator - Joy stack machine execution.

This package provides the Joy evaluator and all primitive operations.

Public API:
    - Evaluator: Main evaluator class for executing Joy programs
    - ExecutionContext: Execution state (stack + evaluator reference)
    - joy_word: Decorator for defining Joy primitives
    - get_primitive: Look up a primitive by name
    - register_primitive: Register a primitive function
    - list_primitives: List all registered primitive names
"""

from __future__ import annotations

# Re-export ExecutionContext from stack module for convenience
from pyjoy.stack import ExecutionContext

# Import all primitive modules to register their words (side-effect imports)
# The order matters for any dependencies between modules
from . import (
    aggregate,  # noqa: F401
    arithmetic,  # noqa: F401
    combinators,  # noqa: F401
    io,  # noqa: F401
    logic,  # noqa: F401
    stack_ops,  # noqa: F401
    system,  # noqa: F401
    types,  # noqa: F401
)

# Import core infrastructure
from .core import (
    Evaluator,
    WordFunc,
    expect_quotation,
    get_primitive,
    joy_word,
    list_primitives,
    register_primitive,
)

__all__ = [
    "Evaluator",
    "ExecutionContext",
    "WordFunc",
    "joy_word",
    "get_primitive",
    "register_primitive",
    "list_primitives",
    "expect_quotation",
]
