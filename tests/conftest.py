"""
pytest configuration and fixtures for pyjoy tests.
"""

import pytest

from pyjoy.stack import JoyStack, ExecutionContext
from pyjoy.evaluator import Evaluator


@pytest.fixture
def stack():
    """Fresh empty stack."""
    return JoyStack()


@pytest.fixture
def ctx():
    """Fresh execution context."""
    return ExecutionContext()


@pytest.fixture
def evaluator():
    """Fresh evaluator with context."""
    return Evaluator()
