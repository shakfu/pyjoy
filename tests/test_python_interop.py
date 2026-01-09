"""
Tests for Python interop (Phase 3).

Tests the following:
- Backtick expression syntax: `expr`
- Dollar expression syntax: $(expr)
- Bang statement syntax: !stmt
- Python namespace management
- Error handling in strict mode
"""

import pytest

from pyjoy.evaluator import Evaluator
from pyjoy.parser import Parser, PythonExpr, PythonStmt
from pyjoy.scanner import Scanner


class TestScannerPythonInterop:
    """Tests for Python interop tokens in scanner."""

    def test_backtick_expr_with_interop(self):
        """Scanner recognizes backtick expressions when python_interop=True."""
        scanner = Scanner(python_interop=True)
        tokens = list(scanner.tokenize("`2 + 3`"))
        assert len(tokens) == 1
        assert tokens[0].type == "PYTHON_EXPR"
        assert tokens[0].value == "2 + 3"

    def test_backtick_expr_without_interop(self):
        """Scanner skips backtick expressions when python_interop=False."""
        scanner = Scanner(python_interop=False)
        tokens = list(scanner.tokenize("`2 + 3`"))
        # Token is skipped
        assert len(tokens) == 0

    def test_dollar_expr_with_interop(self):
        """Scanner recognizes dollar expressions when python_interop=True."""
        scanner = Scanner(python_interop=True)
        tokens = list(scanner.tokenize("$(math.sqrt(16))"))
        assert len(tokens) == 1
        assert tokens[0].type == "PYTHON_DOLLAR"
        assert tokens[0].value == "math.sqrt(16)"

    def test_bang_stmt_with_interop(self):
        """Scanner recognizes bang statements when python_interop=True."""
        scanner = Scanner(python_interop=True)
        tokens = list(scanner.tokenize("!x = 42"))
        assert len(tokens) == 1
        assert tokens[0].type == "PYTHON_STMT"
        assert tokens[0].value == "x = 42"

    def test_mixed_joy_and_python(self):
        """Scanner handles mixed Joy and Python code."""
        scanner = Scanner(python_interop=True)
        tokens = list(scanner.tokenize("1 2 + `3 * 4`"))
        assert len(tokens) == 4
        assert tokens[0].type == "INTEGER"
        assert tokens[1].type == "INTEGER"
        assert tokens[2].type == "SYMBOL"  # +
        assert tokens[3].type == "PYTHON_EXPR"
        assert tokens[3].value == "3 * 4"


class TestParserPythonInterop:
    """Tests for Python interop in parser."""

    def test_parse_backtick_expr(self):
        """Parser creates PythonExpr for backtick syntax."""
        parser = Parser(python_interop=True)
        result = parser.parse_full("`2 + 3`")
        assert len(result.program.terms) == 1
        assert isinstance(result.program.terms[0], PythonExpr)
        assert result.program.terms[0].code == "2 + 3"

    def test_parse_dollar_expr(self):
        """Parser creates PythonExpr for dollar syntax."""
        parser = Parser(python_interop=True)
        result = parser.parse_full("$(x * 2)")
        assert len(result.program.terms) == 1
        assert isinstance(result.program.terms[0], PythonExpr)
        assert result.program.terms[0].code == "x * 2"

    def test_parse_bang_stmt(self):
        """Parser creates PythonStmt for bang syntax."""
        parser = Parser(python_interop=True)
        result = parser.parse_full("!import sys")
        assert len(result.program.terms) == 1
        assert isinstance(result.program.terms[0], PythonStmt)
        assert result.program.terms[0].code == "import sys"

    def test_parse_mixed_code(self):
        """Parser handles mixed Joy and Python code."""
        parser = Parser(python_interop=True)
        result = parser.parse_full("1 2 + `result * 2`")
        terms = result.program.terms
        assert len(terms) == 4
        # 1, 2, +, python_expr
        assert isinstance(terms[3], PythonExpr)


class TestEvaluatorPythonInterop:
    """Tests for Python interop execution in Evaluator."""

    def test_backtick_expr_execution(self):
        """Backtick expression evaluates and pushes result."""
        ev = Evaluator(strict=False)
        ev.run("`2 + 3`")
        assert ev.stack.pop() == 5

    def test_dollar_expr_execution(self):
        """Dollar expression evaluates and pushes result."""
        ev = Evaluator(strict=False)
        ev.run("$(10 * 10)")
        assert ev.stack.pop() == 100

    def test_bang_stmt_execution(self):
        """Bang statement executes without pushing."""
        ev = Evaluator(strict=False)
        initial_depth = ev.stack.depth
        ev.run("!x = 42")
        # Nothing pushed
        assert ev.stack.depth == initial_depth
        # Variable is set in namespace
        assert ev.python_globals["x"] == 42

    def test_math_module_available(self):
        """Math module is pre-imported in pythonic mode."""
        ev = Evaluator(strict=False)
        ev.run("`math.sqrt(16)`")
        assert ev.stack.pop() == 4.0

    def test_stack_access_from_python(self):
        """Can access stack from Python expressions."""
        ev = Evaluator(strict=False)
        ev.run("1 2 3")  # Push 1, 2, 3
        ev.run("`len(stack)`")  # Get stack length
        assert ev.stack.pop() == 3

    def test_stack_manipulation_from_python(self):
        """Can manipulate stack from Python."""
        ev = Evaluator(strict=False)
        ev.run("!stack.push(42)")
        assert ev.stack.pop() == 42

    def test_mixed_joy_and_python(self):
        """Mixed Joy and Python code works together."""
        ev = Evaluator(strict=False)
        ev.run("5 `stack[-1] * 2`")
        # Stack has 5, then 10
        assert ev.stack.pop() == 10
        assert ev.stack.pop() == 5

    def test_variable_persistence(self):
        """Variables persist across statements."""
        ev = Evaluator(strict=False)
        ev.run("!x = 10")
        ev.run("!y = 20")
        ev.run("`x + y`")
        assert ev.stack.pop() == 30

    def test_function_definition(self):
        """Can define Python functions via bang statements."""
        ev = Evaluator(strict=False)
        ev.run("!def square(n): return n * n")
        ev.run("`square(7)`")
        assert ev.stack.pop() == 49

    def test_import_module(self):
        """Can import additional modules."""
        ev = Evaluator(strict=False)
        ev.run("!import sys")
        ev.run("`sys.version_info.major`")
        result = ev.stack.pop()
        assert result >= 3  # Python 3.x

    def test_list_comprehension(self):
        """Python list comprehensions work."""
        ev = Evaluator(strict=False)
        ev.run("`[x * 2 for x in range(5)]`")
        assert ev.stack.pop() == [0, 2, 4, 6, 8]

    def test_dict_creation(self):
        """Can create and use dicts."""
        ev = Evaluator(strict=False)
        ev.run("`{'a': 1, 'b': 2}`")
        d = ev.stack.pop()
        assert d == {"a": 1, "b": 2}


class TestPythonInteropStrictMode:
    """Tests for Python interop error handling in strict mode."""

    def test_strict_mode_ignores_backticks(self):
        """Strict mode parser ignores backtick syntax."""
        parser = Parser(python_interop=False)
        result = parser.parse_full("`2 + 3`")
        # Backticks are not recognized, so nothing is parsed
        assert len(result.program.terms) == 0

    def test_evaluator_strict_no_python_modules(self):
        """Strict mode doesn't pre-import Python modules."""
        ev = Evaluator(strict=True)
        # Math module not in globals
        assert "math" not in ev.python_globals

    def test_evaluator_pythonic_has_modules(self):
        """Pythonic mode pre-imports common modules."""
        ev = Evaluator(strict=False)
        assert "math" in ev.python_globals
        assert "json" in ev.python_globals
        assert "os" in ev.python_globals


class TestPythonInteropNamespace:
    """Tests for Python namespace management."""

    def test_stack_reference_in_namespace(self):
        """Stack is available in namespace."""
        ev = Evaluator(strict=False)
        assert "stack" in ev.python_globals
        assert "S" in ev.python_globals  # Alias
        assert ev.python_globals["stack"] is ev.ctx.stack

    def test_evaluator_reference_in_namespace(self):
        """Evaluator is available in namespace."""
        ev = Evaluator(strict=False)
        assert "evaluator" in ev.python_globals
        assert ev.python_globals["evaluator"] is ev

    def test_ctx_reference_in_namespace(self):
        """ExecutionContext is available in namespace."""
        ev = Evaluator(strict=False)
        assert "ctx" in ev.python_globals
        assert ev.python_globals["ctx"] is ev.ctx

    def test_builtins_available(self):
        """Python builtins are available."""
        ev = Evaluator(strict=False)
        ev.run("`len([1, 2, 3])`")
        assert ev.stack.pop() == 3

        ev.run("`sum([1, 2, 3, 4])`")
        assert ev.stack.pop() == 10


class TestPythonInteropEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_backtick_expr(self):
        """Empty backtick expression."""
        scanner = Scanner(python_interop=True)
        tokens = list(scanner.tokenize("``"))
        assert len(tokens) == 1
        assert tokens[0].value == ""

    def test_complex_python_expression(self):
        """Complex Python expressions work."""
        ev = Evaluator(strict=False)
        ev.run("`(lambda x: x ** 2)(5)`")
        assert ev.stack.pop() == 25

    def test_multiline_not_supported_in_backticks(self):
        """Backticks don't support multiline (by design)."""
        # This is a limitation - backticks are single-line only
        scanner = Scanner(python_interop=True)
        # Newline would end the backtick prematurely
        # Just verify it doesn't crash - behavior is implementation-defined
        _tokens = list(scanner.tokenize("`1 +\n2`"))  # noqa: F841
        # Scanner matches `` (empty) before newline
        # This is expected behavior - use !stmt for multiline

    def test_nested_backticks_not_supported(self):
        """Nested backticks don't work (by design)."""
        scanner = Scanner(python_interop=True)
        # Just verify it doesn't crash - behavior is implementation-defined
        _tokens = list(scanner.tokenize("`f'value: {`x`}'`"))  # noqa: F841
        # The regex will match the first pair of backticks
        # This is expected - avoid nested backticks

    def test_python_error_propagates(self):
        """Python errors propagate correctly."""
        ev = Evaluator(strict=False)
        with pytest.raises(NameError):
            ev.run("`undefined_variable`")

    def test_python_syntax_error_propagates(self):
        """Python syntax errors propagate."""
        ev = Evaluator(strict=False)
        with pytest.raises(SyntaxError):
            ev.run("`def`")  # Invalid Python syntax
