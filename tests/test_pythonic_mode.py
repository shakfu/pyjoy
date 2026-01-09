"""
Tests for non-strict (pythonic) mode.

These tests verify the Phase 1 merger infrastructure:
- PythonStack accepts any Python object
- ExecutionContext with strict=False
- Evaluator with strict=False
- OBJECT type in JoyType
"""

import pytest

from pyjoy.evaluator import Evaluator
from pyjoy.stack import ExecutionContext, JoyStack, PythonStack, StackProtocol
from pyjoy.types import JoyType, JoyValue, python_to_joy


class TestPythonStack:
    """Tests for PythonStack class."""

    def test_push_any_object(self):
        """PythonStack accepts any Python object."""
        stack = PythonStack()
        stack.push(42)
        stack.push("hello")
        stack.push({"key": "value"})
        stack.push([1, 2, 3])
        stack.push(lambda x: x * 2)

        assert stack.depth == 5
        # Pop in reverse order
        fn = stack.pop()
        assert callable(fn)
        assert fn(5) == 10

    def test_push_dict(self):
        """Can push and manipulate dicts."""
        stack = PythonStack()
        stack.push({"a": 1, "b": 2})
        d = stack.pop()
        assert d["a"] == 1
        assert d["b"] == 2

    def test_push_custom_object(self):
        """Can push custom class instances."""

        class MyClass:
            def __init__(self, value):
                self.value = value

        stack = PythonStack()
        obj = MyClass(42)
        stack.push(obj)
        result = stack.pop()
        assert result is obj
        assert result.value == 42

    def test_pop_n_returns_tos_first(self):
        """pop_n returns tuple with TOS first (same as JoyStack)."""
        stack = PythonStack()
        stack.push(1)
        stack.push(2)
        stack.push(3)

        top, second = stack.pop_n(2)
        assert top == 3
        assert second == 2

    def test_peek(self):
        """peek works correctly."""
        stack = PythonStack()
        stack.push("a")
        stack.push("b")
        stack.push("c")

        assert stack.peek(0) == "c"
        assert stack.peek(1) == "b"
        assert stack.peek(2) == "a"

    def test_copy(self):
        """copy creates independent copy."""
        stack = PythonStack()
        stack.push(1)
        stack.push(2)

        copy = stack.copy()
        copy.push(3)

        assert stack.depth == 2
        assert copy.depth == 3

    def test_implements_protocol(self):
        """PythonStack implements StackProtocol."""
        stack = PythonStack()
        assert isinstance(stack, StackProtocol)


class TestJoyStackProtocol:
    """Verify JoyStack also implements StackProtocol."""

    def test_implements_protocol(self):
        """JoyStack implements StackProtocol."""
        stack = JoyStack()
        assert isinstance(stack, StackProtocol)


class TestExecutionContextModes:
    """Tests for ExecutionContext with different modes."""

    def test_strict_mode_uses_joy_stack(self):
        """strict=True creates JoyStack."""
        ctx = ExecutionContext(strict=True)
        assert isinstance(ctx.stack, JoyStack)
        assert ctx.strict is True

    def test_pythonic_mode_uses_python_stack(self):
        """strict=False creates PythonStack."""
        ctx = ExecutionContext(strict=False)
        assert isinstance(ctx.stack, PythonStack)
        assert ctx.strict is False

    def test_default_is_strict(self):
        """Default mode is strict."""
        ctx = ExecutionContext()
        assert ctx.strict is True
        assert isinstance(ctx.stack, JoyStack)

    def test_save_restore_pythonic(self):
        """Save/restore works in pythonic mode."""
        ctx = ExecutionContext(strict=False)
        ctx.stack.push({"a": 1})
        ctx.stack.push([1, 2, 3])

        state_id = ctx.save_stack()
        ctx.stack.push("new item")
        assert ctx.stack.depth == 3

        ctx.restore_stack(state_id)
        assert ctx.stack.depth == 2


class TestEvaluatorModes:
    """Tests for Evaluator with different modes."""

    def test_strict_mode(self):
        """strict=True uses JoyStack and JoyValue wrapping."""
        ev = Evaluator(strict=True)
        assert ev.strict is True
        assert isinstance(ev.ctx.stack, JoyStack)

        ev.run("1 2 3")
        assert ev.ctx.stack.depth == 3
        # Values should be JoyValue instances
        top = ev.ctx.stack.pop()
        assert isinstance(top, JoyValue)
        assert top.type == JoyType.INTEGER
        assert top.value == 3

    def test_pythonic_mode(self):
        """strict=False uses PythonStack."""
        ev = Evaluator(strict=False)
        assert ev.strict is False
        assert isinstance(ev.ctx.stack, PythonStack)

    def test_default_is_strict(self):
        """Default mode is strict."""
        ev = Evaluator()
        assert ev.strict is True

    def test_basic_arithmetic_strict(self):
        """Basic arithmetic works in strict mode."""
        ev = Evaluator(strict=True)
        ev.run("2 3 +")
        result = ev.ctx.stack.pop()
        assert result.value == 5

    def test_basic_arithmetic_pythonic(self):
        """Basic arithmetic works in pythonic mode."""
        ev = Evaluator(strict=False)
        ev.run("2 3 +")
        result = ev.ctx.stack.pop()
        # In pythonic mode, the result is still a JoyValue
        # because primitives return JoyValue
        assert isinstance(result, JoyValue)
        assert result.value == 5


class TestObjectType:
    """Tests for the new OBJECT type."""

    def test_object_type_exists(self):
        """OBJECT type exists in JoyType enum."""
        assert hasattr(JoyType, "OBJECT")

    def test_create_object_value(self):
        """Can create JoyValue with OBJECT type."""
        d = {"key": "value"}
        v = JoyValue.object(d)
        assert v.type == JoyType.OBJECT
        assert v.value is d

    def test_object_repr(self):
        """OBJECT values have appropriate repr."""
        v = JoyValue.object({"key": "value"})
        assert "<object:dict>" in repr(v)

        class MyClass:
            pass

        v = JoyValue.object(MyClass())
        assert "<object:MyClass>" in repr(v)

    def test_object_truthy(self):
        """OBJECT values use Python truthiness."""
        assert JoyValue.object([1, 2, 3]).is_truthy() is True
        assert JoyValue.object([]).is_truthy() is False
        assert JoyValue.object({"a": 1}).is_truthy() is True
        assert JoyValue.object({}).is_truthy() is False
        assert JoyValue.object(0).is_truthy() is False
        assert JoyValue.object(1).is_truthy() is True


class TestPythonToJoy:
    """Tests for python_to_joy with strict parameter."""

    def test_strict_mode_rejects_dict(self):
        """strict=True rejects unconvertible types."""
        with pytest.raises(Exception):
            python_to_joy({"key": "value"}, strict=True)

    def test_non_strict_mode_wraps_dict(self):
        """strict=False wraps dict as OBJECT."""
        d = {"key": "value"}
        v = python_to_joy(d, strict=False)
        assert v.type == JoyType.OBJECT
        assert v.value is d

    def test_non_strict_mode_wraps_custom_object(self):
        """strict=False wraps custom objects as OBJECT."""

        class MyClass:
            pass

        obj = MyClass()
        v = python_to_joy(obj, strict=False)
        assert v.type == JoyType.OBJECT
        assert v.value is obj

    def test_standard_types_work_in_both_modes(self):
        """Standard Joy types work in both modes."""
        # Integer
        assert python_to_joy(42, strict=True).type == JoyType.INTEGER
        assert python_to_joy(42, strict=False).type == JoyType.INTEGER

        # Float
        assert python_to_joy(3.14, strict=True).type == JoyType.FLOAT
        assert python_to_joy(3.14, strict=False).type == JoyType.FLOAT

        # String
        assert python_to_joy("hello", strict=True).type == JoyType.STRING
        assert python_to_joy("hello", strict=False).type == JoyType.STRING

        # Boolean
        assert python_to_joy(True, strict=True).type == JoyType.BOOLEAN
        assert python_to_joy(True, strict=False).type == JoyType.BOOLEAN

    def test_default_is_strict(self):
        """Default mode is strict."""
        with pytest.raises(Exception):
            python_to_joy({"key": "value"})  # Should fail in strict mode
