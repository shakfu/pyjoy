"""
Tests for mode-aware primitive infrastructure (Phase 2).

Tests the following:
- unwrap_value helper function
- wrap_value helper function
- get_numeric helper function
- make_numeric_result helper function
- python_word decorator
- Primitives working in both strict and pythonic modes
"""

import pytest

from pyjoy.evaluator import Evaluator
from pyjoy.evaluator.core import (
    get_numeric,
    is_joy_value,
    make_numeric_result,
    python_word,
    unwrap_value,
    wrap_value,
)
from pyjoy.stack import ExecutionContext
from pyjoy.types import JoyType, JoyValue


class TestUnwrapValue:
    """Tests for unwrap_value helper."""

    def test_unwrap_joy_value(self):
        """Unwraps JoyValue to raw value."""
        jv = JoyValue.integer(42)
        assert unwrap_value(jv) == 42

    def test_unwrap_joy_string(self):
        """Unwraps JoyValue string."""
        jv = JoyValue.string("hello")
        assert unwrap_value(jv) == "hello"

    def test_unwrap_joy_list(self):
        """Unwraps JoyValue list."""
        inner = (JoyValue.integer(1), JoyValue.integer(2))
        jv = JoyValue.list(inner)
        assert unwrap_value(jv) == inner

    def test_unwrap_raw_value(self):
        """Returns raw value unchanged."""
        assert unwrap_value(42) == 42
        assert unwrap_value("hello") == "hello"
        assert unwrap_value([1, 2, 3]) == [1, 2, 3]

    def test_unwrap_dict(self):
        """Returns dict unchanged."""
        d = {"key": "value"}
        assert unwrap_value(d) is d


class TestWrapValue:
    """Tests for wrap_value helper."""

    def test_wrap_strict_mode(self):
        """Wraps value in JoyValue in strict mode."""
        result = wrap_value(42, strict=True)
        assert isinstance(result, JoyValue)
        assert result.type == JoyType.INTEGER
        assert result.value == 42

    def test_wrap_pythonic_mode(self):
        """Returns raw value in pythonic mode."""
        result = wrap_value(42, strict=False)
        assert result == 42
        assert not isinstance(result, JoyValue)

    def test_wrap_string_strict(self):
        """Wraps string correctly in strict mode."""
        result = wrap_value("hello", strict=True)
        assert result.type == JoyType.STRING
        assert result.value == "hello"


class TestGetNumeric:
    """Tests for get_numeric helper."""

    def test_get_from_joy_integer(self):
        """Extracts int from JoyValue INTEGER."""
        jv = JoyValue.integer(42)
        assert get_numeric(jv) == 42

    def test_get_from_joy_float(self):
        """Extracts float from JoyValue FLOAT."""
        jv = JoyValue.floating(3.14)
        assert get_numeric(jv) == 3.14

    def test_get_from_joy_char(self):
        """Converts char to ordinal."""
        jv = JoyValue.char("A")
        assert get_numeric(jv) == 65

    def test_get_from_joy_boolean(self):
        """Converts boolean to 0/1."""
        assert get_numeric(JoyValue.boolean(True)) == 1
        assert get_numeric(JoyValue.boolean(False)) == 0

    def test_get_from_raw_int(self):
        """Handles raw int."""
        assert get_numeric(42) == 42

    def test_get_from_raw_float(self):
        """Handles raw float."""
        assert get_numeric(3.14) == 3.14

    def test_get_from_raw_bool(self):
        """Handles raw bool."""
        assert get_numeric(True) == 1
        assert get_numeric(False) == 0

    def test_get_from_raw_char(self):
        """Handles raw single char string."""
        assert get_numeric("A") == 65

    def test_invalid_type_raises(self):
        """Raises on non-numeric type."""
        from pyjoy.errors import JoyTypeError

        with pytest.raises(JoyTypeError):
            get_numeric(JoyValue.string("hello"))

        with pytest.raises(JoyTypeError):
            get_numeric("hello")  # Multi-char string


class TestMakeNumericResult:
    """Tests for make_numeric_result helper."""

    def test_integer_strict(self):
        """Creates JoyValue INTEGER in strict mode."""
        result = make_numeric_result(42, strict=True)
        assert isinstance(result, JoyValue)
        assert result.type == JoyType.INTEGER
        assert result.value == 42

    def test_float_strict(self):
        """Creates JoyValue FLOAT in strict mode."""
        result = make_numeric_result(3.14, strict=True)
        assert result.type == JoyType.FLOAT
        assert result.value == 3.14

    def test_whole_float_becomes_integer(self):
        """Float with .0 becomes INTEGER in strict mode."""
        result = make_numeric_result(5.0, strict=True)
        assert result.type == JoyType.INTEGER
        assert result.value == 5

    def test_pythonic_mode_returns_raw(self):
        """Returns raw value in pythonic mode."""
        assert make_numeric_result(42, strict=False) == 42
        assert make_numeric_result(3.14, strict=False) == 3.14


class TestIsJoyValue:
    """Tests for is_joy_value helper."""

    def test_joy_value_returns_true(self):
        """Returns True for JoyValue."""
        assert is_joy_value(JoyValue.integer(42)) is True

    def test_raw_value_returns_false(self):
        """Returns False for raw value."""
        assert is_joy_value(42) is False
        assert is_joy_value("hello") is False
        assert is_joy_value([1, 2, 3]) is False


class TestPythonWordDecorator:
    """Tests for @python_word decorator."""

    def test_simple_add_strict(self):
        """Simple add function works in strict mode."""

        @python_word(name="test_add")
        def test_add(a, b):
            return a + b

        ctx = ExecutionContext(strict=True)
        ctx.stack.push(3)
        ctx.stack.push(4)

        test_add(ctx)

        result = ctx.stack.pop()
        assert isinstance(result, JoyValue)
        assert result.value == 7

    def test_simple_add_pythonic(self):
        """Simple add function works in pythonic mode."""

        @python_word(name="test_add2")
        def test_add2(a, b):
            return a + b

        ctx = ExecutionContext(strict=False)
        ctx.stack.push(3)
        ctx.stack.push(4)

        test_add2(ctx)

        result = ctx.stack.pop()
        assert result == 7
        assert not isinstance(result, JoyValue)

    def test_single_arg_function(self):
        """Single argument function works."""

        @python_word(name="test_double")
        def test_double(x):
            return x * 2

        ctx = ExecutionContext(strict=True)
        ctx.stack.push(5)

        test_double(ctx)

        result = ctx.stack.pop()
        assert result.value == 10

    def test_no_arg_function(self):
        """Zero argument function works."""

        @python_word(name="test_const")
        def test_const():
            return 42

        ctx = ExecutionContext(strict=True)

        test_const(ctx)

        result = ctx.stack.pop()
        assert result.value == 42

    def test_none_result_not_pushed(self):
        """None result is not pushed."""

        @python_word(name="test_none")
        def test_none(x):
            return None

        ctx = ExecutionContext(strict=True)
        ctx.stack.push(5)
        initial_depth = ctx.stack.depth

        test_none(ctx)

        # Stack depth should be 0 (value consumed, nothing pushed)
        assert ctx.stack.depth == initial_depth - 1

    def test_three_arg_function(self):
        """Three argument function works."""

        @python_word(name="test_ternary")
        def test_ternary(a, b, c):
            return a + b + c

        ctx = ExecutionContext(strict=True)
        ctx.stack.push(1)
        ctx.stack.push(2)
        ctx.stack.push(3)

        test_ternary(ctx)

        result = ctx.stack.pop()
        assert result.value == 6

    def test_stack_underflow_raises(self):
        """Stack underflow raises appropriate error."""
        from pyjoy.errors import JoyStackUnderflow

        @python_word(name="test_underflow")
        def test_underflow(a, b):
            return a + b

        ctx = ExecutionContext(strict=True)
        ctx.stack.push(5)  # Only one value

        with pytest.raises(JoyStackUnderflow):
            test_underflow(ctx)

    def test_string_concatenation(self):
        """Works with string operations."""

        @python_word(name="test_concat")
        def test_concat(a, b):
            return str(a) + str(b)

        ctx = ExecutionContext(strict=True)
        ctx.stack.push("hello")
        ctx.stack.push("world")

        test_concat(ctx)

        result = ctx.stack.pop()
        assert result.value == "helloworld"


class TestPrimitivesInBothModes:
    """Test that existing primitives work in both modes."""

    def test_arithmetic_strict(self):
        """Arithmetic works in strict mode."""
        ev = Evaluator(strict=True)
        ev.run("10 3 +")
        assert ev.stack.pop().value == 13

        ev.run("10 3 -")
        assert ev.stack.pop().value == 7

        ev.run("10 3 *")
        assert ev.stack.pop().value == 30

        ev.run("10 3 /")
        assert ev.stack.pop().value == 3

    def test_arithmetic_pythonic(self):
        """Arithmetic works in pythonic mode."""
        ev = Evaluator(strict=False)
        ev.run("10 3 +")
        result = ev.stack.pop()
        # Result is still JoyValue because primitives create JoyValue
        assert result.value == 13

    def test_stack_ops_strict(self):
        """Stack operations work in strict mode."""
        ev = Evaluator(strict=True)
        ev.run("1 2 dup")
        assert ev.stack.depth == 3
        assert ev.stack.pop().value == 2
        assert ev.stack.pop().value == 2

    def test_stack_ops_pythonic(self):
        """Stack operations work in pythonic mode."""
        ev = Evaluator(strict=False)
        ev.run("1 2 dup")
        assert ev.stack.depth == 3

    def test_comparison_strict(self):
        """Comparison works in strict mode."""
        ev = Evaluator(strict=True)
        ev.run("5 3 >")
        assert ev.stack.pop().value is True

        ev.run("3 5 >")
        assert ev.stack.pop().value is False

    def test_quotation_execution_strict(self):
        """Quotation execution works in strict mode."""
        ev = Evaluator(strict=True)
        ev.run("[2 3 +] i")
        assert ev.stack.pop().value == 5

    def test_ifte_strict(self):
        """Conditional works in strict mode."""
        ev = Evaluator(strict=True)
        ev.run("5 [0 >] [1] [0] ifte")
        assert ev.stack.pop().value == 1

        ev.run("-5 [0 >] [1] [0] ifte")
        assert ev.stack.pop().value == 0


class TestMixedModeValues:
    """Test handling of mixed JoyValue and raw values."""

    def test_pythonic_stack_with_joy_values(self):
        """Pythonic stack can contain JoyValue objects."""
        ev = Evaluator(strict=False)
        # Push a JoyValue directly
        ev.ctx.stack.push(JoyValue.integer(42))
        ev.ctx.stack.push(10)

        # Run add - should handle mixed types
        ev.run("+")
        result = ev.stack.pop()
        # The primitive extracts values correctly
        assert result.value == 52

    def test_unwrap_handles_nested_structures(self):
        """unwrap_value handles JoyValue in complex scenarios."""
        # Nested JoyValue list
        inner = (JoyValue.integer(1), JoyValue.integer(2))
        jv = JoyValue.list(inner)

        raw = unwrap_value(jv)
        # Returns the tuple (which still contains JoyValues)
        assert raw == inner
