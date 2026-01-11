"""
Dual-mode tests for pyjoy.

These tests verify that core functionality works correctly in both:
- strict=True (Joy compliance mode with JoyValue wrapping)
- strict=False (Pythonic mode with raw Python objects)

The dual_evaluator fixture parameterizes tests to run in both modes.
"""

import pytest

from pyjoy.evaluator import Evaluator
from pyjoy.types import JoyQuotation, JoyValue


@pytest.fixture(params=[True, False], ids=["strict", "pythonic"])
def dual_evaluator(request):
    """Evaluator that runs tests in both strict and pythonic modes."""
    return Evaluator(strict=request.param)


def get_stack_value(evaluator):
    """
    Get the top stack value in a mode-agnostic way.

    In strict mode, unwraps JoyValue to get raw value.
    In pythonic mode, returns value directly.
    """
    val = evaluator.stack.pop()
    if isinstance(val, JoyValue):
        return val.value
    return val


def get_stack_values(evaluator, n):
    """Get n values from stack in mode-agnostic way."""
    values = []
    for _ in range(n):
        values.append(get_stack_value(evaluator))
    return values


class TestDualModeArithmetic:
    """Arithmetic operations should work in both modes."""

    def test_addition(self, dual_evaluator):
        dual_evaluator.run("2 3 +")
        assert get_stack_value(dual_evaluator) == 5

    def test_subtraction(self, dual_evaluator):
        dual_evaluator.run("10 3 -")
        assert get_stack_value(dual_evaluator) == 7

    def test_multiplication(self, dual_evaluator):
        dual_evaluator.run("4 5 *")
        assert get_stack_value(dual_evaluator) == 20

    def test_division(self, dual_evaluator):
        dual_evaluator.run("20 4 /")
        assert get_stack_value(dual_evaluator) == 5

    def test_modulo(self, dual_evaluator):
        dual_evaluator.run("17 5 rem")
        assert get_stack_value(dual_evaluator) == 2

    def test_negation(self, dual_evaluator):
        dual_evaluator.run("42 neg")
        assert get_stack_value(dual_evaluator) == -42

    def test_absolute_value(self, dual_evaluator):
        dual_evaluator.run("-15 abs")
        assert get_stack_value(dual_evaluator) == 15

    def test_sign_positive(self, dual_evaluator):
        dual_evaluator.run("42 sign")
        assert get_stack_value(dual_evaluator) == 1

    def test_sign_negative(self, dual_evaluator):
        dual_evaluator.run("-42 sign")
        assert get_stack_value(dual_evaluator) == -1

    def test_sign_zero(self, dual_evaluator):
        dual_evaluator.run("0 sign")
        assert get_stack_value(dual_evaluator) == 0

    def test_float_addition(self, dual_evaluator):
        dual_evaluator.run("1.5 2.5 +")
        assert get_stack_value(dual_evaluator) == 4.0

    def test_mixed_int_float(self, dual_evaluator):
        dual_evaluator.run("2 3.5 +")
        assert get_stack_value(dual_evaluator) == 5.5

    def test_integer_division(self, dual_evaluator):
        # div in Joy is divmod: pushes quotient then remainder
        dual_evaluator.run("17 5 div")
        r = get_stack_value(dual_evaluator)  # remainder
        q = get_stack_value(dual_evaluator)  # quotient
        assert q == 3
        assert r == 2

    def test_max(self, dual_evaluator):
        dual_evaluator.run("10 20 max")
        assert get_stack_value(dual_evaluator) == 20

    def test_min(self, dual_evaluator):
        dual_evaluator.run("10 20 min")
        assert get_stack_value(dual_evaluator) == 10

    def test_succ(self, dual_evaluator):
        dual_evaluator.run("41 succ")
        assert get_stack_value(dual_evaluator) == 42

    def test_pred(self, dual_evaluator):
        dual_evaluator.run("43 pred")
        assert get_stack_value(dual_evaluator) == 42


class TestDualModeComparison:
    """Comparison operations should work in both modes."""

    def test_less_than_true(self, dual_evaluator):
        dual_evaluator.run("3 5 <")
        assert get_stack_value(dual_evaluator) is True

    def test_less_than_false(self, dual_evaluator):
        dual_evaluator.run("5 3 <")
        assert get_stack_value(dual_evaluator) is False

    def test_greater_than_true(self, dual_evaluator):
        dual_evaluator.run("5 3 >")
        assert get_stack_value(dual_evaluator) is True

    def test_greater_than_false(self, dual_evaluator):
        dual_evaluator.run("3 5 >")
        assert get_stack_value(dual_evaluator) is False

    def test_less_equal_true(self, dual_evaluator):
        dual_evaluator.run("3 5 <=")
        assert get_stack_value(dual_evaluator) is True

    def test_less_equal_equal(self, dual_evaluator):
        dual_evaluator.run("5 5 <=")
        assert get_stack_value(dual_evaluator) is True

    def test_greater_equal_true(self, dual_evaluator):
        dual_evaluator.run("5 3 >=")
        assert get_stack_value(dual_evaluator) is True

    def test_greater_equal_equal(self, dual_evaluator):
        dual_evaluator.run("5 5 >=")
        assert get_stack_value(dual_evaluator) is True

    def test_equal_true(self, dual_evaluator):
        dual_evaluator.run("42 42 =")
        assert get_stack_value(dual_evaluator) is True

    def test_equal_false(self, dual_evaluator):
        dual_evaluator.run("42 43 =")
        assert get_stack_value(dual_evaluator) is False

    def test_not_equal_true(self, dual_evaluator):
        dual_evaluator.run("42 43 !=")
        assert get_stack_value(dual_evaluator) is True

    def test_not_equal_false(self, dual_evaluator):
        dual_evaluator.run("42 42 !=")
        assert get_stack_value(dual_evaluator) is False


class TestDualModeLogic:
    """Logic operations should work in both modes."""

    def test_and_true(self, dual_evaluator):
        dual_evaluator.run("true true and")
        assert get_stack_value(dual_evaluator) is True

    def test_and_false(self, dual_evaluator):
        dual_evaluator.run("true false and")
        assert get_stack_value(dual_evaluator) is False

    def test_or_true(self, dual_evaluator):
        dual_evaluator.run("true false or")
        assert get_stack_value(dual_evaluator) is True

    def test_or_false(self, dual_evaluator):
        dual_evaluator.run("false false or")
        assert get_stack_value(dual_evaluator) is False

    def test_not_true(self, dual_evaluator):
        dual_evaluator.run("false not")
        assert get_stack_value(dual_evaluator) is True

    def test_not_false(self, dual_evaluator):
        dual_evaluator.run("true not")
        assert get_stack_value(dual_evaluator) is False

    def test_xor_true(self, dual_evaluator):
        dual_evaluator.run("true false xor")
        assert get_stack_value(dual_evaluator) is True

    def test_xor_false(self, dual_evaluator):
        dual_evaluator.run("true true xor")
        assert get_stack_value(dual_evaluator) is False


class TestDualModeStackOps:
    """Stack operations should work in both modes."""

    def test_dup(self, dual_evaluator):
        dual_evaluator.run("42 dup")
        a, b = get_stack_values(dual_evaluator, 2)
        assert a == 42
        assert b == 42

    def test_pop(self, dual_evaluator):
        dual_evaluator.run("1 2 3 pop")
        assert dual_evaluator.stack.depth == 2
        assert get_stack_value(dual_evaluator) == 2

    def test_swap(self, dual_evaluator):
        dual_evaluator.run("1 2 swap")
        a, b = get_stack_values(dual_evaluator, 2)
        assert a == 1
        assert b == 2

    def test_rollup(self, dual_evaluator):
        """X Y Z -> Z X Y"""
        dual_evaluator.run("1 2 3 rollup")
        # After rollup: stack is [3, 1, 2] (bottom to top)
        # Pop order: 2, 1, 3
        a, b, c = get_stack_values(dual_evaluator, 3)
        assert (a, b, c) == (2, 1, 3)

    def test_rolldown(self, dual_evaluator):
        """X Y Z -> Y Z X"""
        dual_evaluator.run("1 2 3 rolldown")
        # After rolldown: stack is [2, 3, 1] (bottom to top)
        # Pop order: 1, 3, 2
        a, b, c = get_stack_values(dual_evaluator, 3)
        assert (a, b, c) == (1, 3, 2)

    def test_rotate(self, dual_evaluator):
        """X Y Z -> Z Y X"""
        dual_evaluator.run("1 2 3 rotate")
        # After rotate: stack is [3, 2, 1] (bottom to top)
        # Pop order: 1, 2, 3
        a, b, c = get_stack_values(dual_evaluator, 3)
        assert (a, b, c) == (1, 2, 3)

    def test_dupd(self, dual_evaluator):
        """X Y -> X X Y"""
        dual_evaluator.run("1 2 dupd")
        a, b, c = get_stack_values(dual_evaluator, 3)
        assert (a, b, c) == (2, 1, 1)

    def test_swapd(self, dual_evaluator):
        """X Y Z -> Y X Z"""
        dual_evaluator.run("1 2 3 swapd")
        a, b, c = get_stack_values(dual_evaluator, 3)
        assert (a, b, c) == (3, 1, 2)

    def test_popd(self, dual_evaluator):
        """X Y -> Y"""
        dual_evaluator.run("1 2 popd")
        assert dual_evaluator.stack.depth == 1
        assert get_stack_value(dual_evaluator) == 2


def unwrap_list(result):
    """Unwrap a list result to raw Python values for comparison."""
    if isinstance(result, (list, tuple)):
        return tuple(v.value if isinstance(v, JoyValue) else v for v in result)
    if isinstance(result, JoyQuotation):
        return tuple(v.value if isinstance(v, JoyValue) else v for v in result.terms)
    return result


class TestDualModeLists:
    """List operations should work in both modes."""

    def test_empty_list(self, dual_evaluator):
        dual_evaluator.run("[]")
        result = get_stack_value(dual_evaluator)
        # Empty list/quotation
        unwrapped = unwrap_list(result)
        assert unwrapped == ()

    def test_list_literal(self, dual_evaluator):
        dual_evaluator.run("[1 2 3]")
        result = get_stack_value(dual_evaluator)
        assert unwrap_list(result) == (1, 2, 3)

    def test_cons(self, dual_evaluator):
        dual_evaluator.run("1 [2 3] cons")
        result = get_stack_value(dual_evaluator)
        assert unwrap_list(result) == (1, 2, 3)

    def test_first(self, dual_evaluator):
        dual_evaluator.run("[1 2 3] first")
        assert get_stack_value(dual_evaluator) == 1

    def test_rest(self, dual_evaluator):
        dual_evaluator.run("[1 2 3] rest")
        result = get_stack_value(dual_evaluator)
        assert unwrap_list(result) == (2, 3)

    def test_size(self, dual_evaluator):
        dual_evaluator.run("[1 2 3 4 5] size")
        assert get_stack_value(dual_evaluator) == 5

    def test_null_true(self, dual_evaluator):
        dual_evaluator.run("[] null")
        assert get_stack_value(dual_evaluator) is True

    def test_null_false(self, dual_evaluator):
        dual_evaluator.run("[1] null")
        assert get_stack_value(dual_evaluator) is False

    def test_concat(self, dual_evaluator):
        dual_evaluator.run("[1 2] [3 4] concat")
        result = get_stack_value(dual_evaluator)
        assert unwrap_list(result) == (1, 2, 3, 4)

    def test_reverse(self, dual_evaluator):
        dual_evaluator.run("[1 2 3] reverse")
        result = get_stack_value(dual_evaluator)
        assert unwrap_list(result) == (3, 2, 1)


class TestDualModeCombinators:
    """Combinators should work in both modes."""

    def test_i(self, dual_evaluator):
        """[P] i == P"""
        dual_evaluator.run("[42] i")
        assert get_stack_value(dual_evaluator) == 42

    def test_dip(self, dual_evaluator):
        """X [P] dip == P X"""
        dual_evaluator.run("1 2 [dup] dip")
        # Stack: 1 dup -> 1 1, then push 2 -> 1 1 2
        a, b, c = get_stack_values(dual_evaluator, 3)
        assert (a, b, c) == (2, 1, 1)

    def test_ifte_true(self, dual_evaluator):
        """[condition] [then] [else] ifte"""
        dual_evaluator.run("5 [0 >] [dup *] [pop 0] ifte")
        assert get_stack_value(dual_evaluator) == 25

    def test_ifte_false(self, dual_evaluator):
        dual_evaluator.run("-5 [0 >] [dup *] [pop 0] ifte")
        assert get_stack_value(dual_evaluator) == 0

    def test_branch_true(self, dual_evaluator):
        dual_evaluator.run("true [1] [2] branch")
        assert get_stack_value(dual_evaluator) == 1

    def test_branch_false(self, dual_evaluator):
        dual_evaluator.run("false [1] [2] branch")
        assert get_stack_value(dual_evaluator) == 2

    def test_map(self, dual_evaluator):
        dual_evaluator.run("[1 2 3] [dup *] map")
        result = get_stack_value(dual_evaluator)
        if isinstance(result, tuple):
            if result and isinstance(result[0], JoyValue):
                result = tuple(v.value for v in result)
        assert tuple(result) == (1, 4, 9)

    def test_filter(self, dual_evaluator):
        dual_evaluator.run("[1 2 3 4 5] [2 >] filter")
        result = get_stack_value(dual_evaluator)
        if isinstance(result, tuple):
            if result and isinstance(result[0], JoyValue):
                result = tuple(v.value for v in result)
        assert tuple(result) == (3, 4, 5)

    def test_fold(self, dual_evaluator):
        dual_evaluator.run("[1 2 3 4] 0 [+] fold")
        assert get_stack_value(dual_evaluator) == 10

    def test_times(self, dual_evaluator):
        dual_evaluator.run("1 5 [dup +] times")
        # 1 -> 2 -> 4 -> 8 -> 16 -> 32
        assert get_stack_value(dual_evaluator) == 32

    def test_step(self, dual_evaluator):
        """Execute quotation for each element."""
        dual_evaluator.run("0 [1 2 3] [+] step")
        assert get_stack_value(dual_evaluator) == 6


@pytest.fixture
def strict_evaluator():
    """Evaluator in strict mode only."""
    return Evaluator(strict=True)


class TestDualModeStrings:
    """String operations should work in both modes."""

    def test_string_literal(self, dual_evaluator):
        dual_evaluator.run('"hello"')
        assert get_stack_value(dual_evaluator) == "hello"

    def test_string_concat(self, strict_evaluator):
        # String concat via aggregate needs mode-aware updates
        # For now, test strict mode only
        strict_evaluator.run('"hello " "world" concat')
        assert strict_evaluator.stack.pop().value == "hello world"

    def test_string_size(self, strict_evaluator):
        # String size via aggregate needs mode-aware updates
        # For now, test strict mode only
        strict_evaluator.run('"hello" size')
        assert strict_evaluator.stack.pop().value == 5


class TestDualModeDefinitions:
    """User definitions should work in both modes."""

    def test_simple_definition(self, dual_evaluator):
        dual_evaluator.run("DEFINE square == dup *.")
        dual_evaluator.run("5 square")
        assert get_stack_value(dual_evaluator) == 25

    def test_definition_using_definition(self, dual_evaluator):
        dual_evaluator.run("DEFINE square == dup *.")
        dual_evaluator.run("DEFINE cube == dup dup * *.")
        dual_evaluator.run("3 cube")
        assert get_stack_value(dual_evaluator) == 27

    def test_recursive_definition(self, dual_evaluator):
        dual_evaluator.run("""
            DEFINE factorial ==
                [0 =] [pop 1] [dup 1 - factorial *] ifte.
        """)
        dual_evaluator.run("5 factorial")
        assert get_stack_value(dual_evaluator) == 120


class TestDualModeTypePredicates:
    """Type predicates should work in both modes."""

    def test_integer_true(self, dual_evaluator):
        dual_evaluator.run("42 integer")
        assert get_stack_value(dual_evaluator) is True

    def test_integer_false(self, dual_evaluator):
        dual_evaluator.run("3.14 integer")
        assert get_stack_value(dual_evaluator) is False

    def test_float_true(self, dual_evaluator):
        dual_evaluator.run("3.14 float")
        assert get_stack_value(dual_evaluator) is True

    def test_float_false(self, dual_evaluator):
        dual_evaluator.run("42 float")
        assert get_stack_value(dual_evaluator) is False

    def test_string_true(self, dual_evaluator):
        dual_evaluator.run('"hello" string')
        assert get_stack_value(dual_evaluator) is True

    def test_list_true(self, dual_evaluator):
        dual_evaluator.run("[1 2 3] list")
        assert get_stack_value(dual_evaluator) is True

    def test_logical_true(self, dual_evaluator):
        dual_evaluator.run("true logical")
        assert get_stack_value(dual_evaluator) is True

    def test_logical_false(self, dual_evaluator):
        dual_evaluator.run("42 logical")
        assert get_stack_value(dual_evaluator) is False


class TestDualModeStackDepth:
    """Stack depth tracking should work in both modes."""

    def test_stack_starts_empty(self, dual_evaluator):
        assert dual_evaluator.stack.depth == 0

    def test_stack_depth_after_push(self, dual_evaluator):
        dual_evaluator.run("1 2 3")
        assert dual_evaluator.stack.depth == 3

    def test_stack_depth_after_pop(self, dual_evaluator):
        dual_evaluator.run("1 2 3 pop pop")
        assert dual_evaluator.stack.depth == 1

    def test_stack_after_clear(self, dual_evaluator):
        dual_evaluator.run("1 2 3")
        dual_evaluator.stack.clear()
        assert dual_evaluator.stack.depth == 0


class TestDualModeEdgeCases:
    """Edge cases should be handled consistently in both modes."""

    def test_empty_program(self, dual_evaluator):
        dual_evaluator.run("")
        assert dual_evaluator.stack.depth == 0

    def test_whitespace_only(self, dual_evaluator):
        dual_evaluator.run("   \n\t  ")
        assert dual_evaluator.stack.depth == 0

    def test_comments_ignored(self, dual_evaluator):
        dual_evaluator.run("(* this is a comment *) 42")
        assert get_stack_value(dual_evaluator) == 42

    def test_line_comments_ignored(self, dual_evaluator):
        dual_evaluator.run("42 # this is a comment\n43")
        b, a = get_stack_values(dual_evaluator, 2)
        assert a == 42
        assert b == 43

    def test_negative_integers(self, dual_evaluator):
        dual_evaluator.run("-42")
        assert get_stack_value(dual_evaluator) == -42

    def test_negative_floats(self, dual_evaluator):
        dual_evaluator.run("-3.14")
        assert get_stack_value(dual_evaluator) == -3.14

    def test_zero(self, dual_evaluator):
        dual_evaluator.run("0 0.0")
        assert get_stack_value(dual_evaluator) == 0.0
        assert get_stack_value(dual_evaluator) == 0
