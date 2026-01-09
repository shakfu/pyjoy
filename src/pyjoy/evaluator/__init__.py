"""
pyjoy.evaluator - Joy stack machine execution.

This package provides the Joy evaluator and all primitive operations.

Public API:
    - Evaluator: Main evaluator class for executing Joy programs
    - ExecutionContext: Execution state (stack + evaluator reference)
    - joy_word: Decorator for defining Joy primitives (full control)
    - python_word: Decorator for simple auto-pop/push primitives
    - get_primitive: Look up a primitive by name
    - register_primitive: Register a primitive function
    - list_primitives: List all registered primitive names

Mode-Aware Helpers:
    - unwrap_value: Extract raw value from JoyValue or return as-is
    - wrap_value: Wrap raw value in JoyValue based on mode
    - get_numeric: Extract numeric value from JoyValue or raw value
    - make_numeric_result: Create appropriate numeric result for mode
    - is_joy_value: Check if value is a JoyValue instance
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
    PythonInteropError,
    WordFunc,
    expect_quotation,
    get_numeric,
    get_primitive,
    is_joy_value,
    joy_word,
    list_primitives,
    make_numeric_result,
    python_word,
    register_primitive,
    unwrap_value,
    wrap_value,
)

__all__ = [
    # Core classes
    "Evaluator",
    "ExecutionContext",
    "WordFunc",
    # Decorators
    "joy_word",
    "python_word",
    # Registry functions
    "get_primitive",
    "register_primitive",
    "list_primitives",
    # Helper functions
    "expect_quotation",
    "unwrap_value",
    "wrap_value",
    "get_numeric",
    "make_numeric_result",
    "is_joy_value",
    # Exceptions
    "PythonInteropError",
]
