"""
pyjoy.evaluator - Joy stack machine execution.

Executes Joy programs by iterating through terms and manipulating the stack.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Optional

from pyjoy.errors import (
    JoyUndefinedWord,
    JoyStackUnderflow,
    JoyTypeError,
    JoyDivisionByZero,
    JoyEmptyAggregate,
)
from pyjoy.parser import parse
from pyjoy.stack import ExecutionContext
from pyjoy.types import JoyValue, JoyQuotation, JoyType


# Type alias for Joy word implementations
WordFunc = Callable[[ExecutionContext], None]

# Global registry for primitive words
_primitives: Dict[str, WordFunc] = {}


def joy_word(
    name: Optional[str] = None,
    params: int = 0,
    doc: Optional[str] = None,
) -> Callable[[Callable[..., None]], WordFunc]:
    """
    Decorator to define a Joy word implemented in Python.

    Args:
        name: Joy word name (defaults to function name)
        params: Required stack parameters
        doc: Documentation string (Joy signature like "X Y -> Z")

    Example:
        @joy_word(name="+", params=2, doc="N1 N2 -> N3")
        def plus(ctx):
            b, a = ctx.stack.pop_n(2)
            result = a.value + b.value
            ctx.stack.push(result)
    """

    def decorator(func: Callable[..., None]) -> WordFunc:
        word_name = name or func.__name__

        @wraps(func)
        def wrapper(ctx: ExecutionContext) -> None:
            # Validate parameter count
            if ctx.stack.depth < params:
                raise JoyStackUnderflow(word_name, params, ctx.stack.depth)

            # Execute the primitive
            func(ctx)

        # Store metadata on the wrapper
        wrapper.joy_word = word_name  # type: ignore[attr-defined]
        wrapper.joy_params = params  # type: ignore[attr-defined]
        wrapper.joy_doc = doc or func.__doc__  # type: ignore[attr-defined]

        # Register in global primitives
        _primitives[word_name] = wrapper
        return wrapper

    return decorator


def get_primitive(name: str) -> Optional[WordFunc]:
    """Get a registered primitive by name."""
    return _primitives.get(name)


def register_primitive(name: str, func: WordFunc) -> None:
    """Register a primitive without using the decorator."""
    _primitives[name] = func


def list_primitives() -> list[str]:
    """List all registered primitive names."""
    return sorted(_primitives.keys())


class Evaluator:
    """
    Joy evaluator: executes programs on a stack.

    Manages:
    - Execution context (stack + saved states)
    - User-defined words
    - Program execution
    """

    def __init__(self) -> None:
        self.ctx = ExecutionContext()
        self.ctx.set_evaluator(self)
        self.definitions: Dict[str, JoyQuotation] = {}

    def execute(self, program: JoyQuotation) -> None:
        """
        Execute a Joy program (quotation).

        Args:
            program: JoyQuotation to execute
        """
        for term in program.terms:
            self._execute_term(term)

    def run(self, source: str) -> None:
        """
        Parse and execute Joy source code.

        Args:
            source: Joy source code string
        """
        program = parse(source)
        self.execute(program)

    def _execute_term(self, term: Any) -> None:
        """
        Execute a single term.

        Args:
            term: Can be JoyValue, JoyQuotation, or string (symbol)
        """
        if isinstance(term, JoyValue):
            # Literal value: push to stack
            self.ctx.stack.push_value(term)

        elif isinstance(term, JoyQuotation):
            # Quotation: wrap and push (don't execute)
            self.ctx.stack.push_value(JoyValue.quotation(term))

        elif isinstance(term, str):
            # Symbol: look up and execute
            self._execute_symbol(term)

        else:
            # Unknown: try to convert and push
            self.ctx.stack.push(term)

    def _execute_symbol(self, name: str) -> None:
        """
        Look up and execute a symbol.

        Args:
            name: Symbol name

        Raises:
            JoyUndefinedWord: If symbol is not defined
        """
        # Check primitives first
        primitive = get_primitive(name)
        if primitive is not None:
            primitive(self.ctx)
            return

        # Check user definitions
        if name in self.definitions:
            self.execute(self.definitions[name])
            return

        raise JoyUndefinedWord(name)

    def define(self, name: str, body: JoyQuotation) -> None:
        """
        Define a new word.

        Args:
            name: Word name
            body: Word body as a quotation
        """
        self.definitions[name] = body

    def execute_quotation(self, quot: JoyValue) -> None:
        """
        Execute a quotation value from the stack.

        Used by combinators like 'i'.

        Args:
            quot: JoyValue of type QUOTATION

        Raises:
            JoyTypeError: If quot is not a quotation
        """
        if quot.type != JoyType.QUOTATION:
            raise JoyTypeError("execute_quotation", "QUOTATION", quot.type.name)
        self.execute(quot.value)

    @property
    def stack(self):
        """Convenience access to the stack."""
        return self.ctx.stack


# ============================================================================
# Basic Primitives (Phase 1 - minimal set for testing)
# ============================================================================

# Stack Operations

@joy_word(name="dup", params=1, doc="X -> X X")
def dup(ctx: ExecutionContext) -> None:
    """Duplicate top of stack."""
    top = ctx.stack.peek()
    ctx.stack.push_value(top)


@joy_word(name="pop", params=1, doc="X ->")
def pop(ctx: ExecutionContext) -> None:
    """Remove top of stack."""
    ctx.stack.pop()


@joy_word(name="swap", params=2, doc="X Y -> Y X")
def swap(ctx: ExecutionContext) -> None:
    """Exchange top two stack items."""
    b, a = ctx.stack.pop_n(2)
    ctx.stack.push_value(b)
    ctx.stack.push_value(a)


@joy_word(name="stack", params=0, doc=".. -> .. [..]")
def stack_word(ctx: ExecutionContext) -> None:
    """Push a list of the current stack contents."""
    items = tuple(ctx.stack.items())
    ctx.stack.push_value(JoyValue.list(items))


@joy_word(name="unstack", params=1, doc="[X Y ..] -> X Y ..")
def unstack(ctx: ExecutionContext) -> None:
    """Replace stack with contents of list/quotation on top."""
    lst = ctx.stack.pop()
    if lst.type == JoyType.LIST:
        items = lst.value
    elif lst.type == JoyType.QUOTATION:
        # Quotation terms can be executed as a list
        items = lst.value.terms
    else:
        raise JoyTypeError("unstack", "LIST or QUOTATION", lst.type.name)
    ctx.stack.clear()
    for item in items:
        if isinstance(item, JoyValue):
            ctx.stack.push_value(item)
        else:
            # Symbol or other term - push as-is
            ctx.stack.push(item)


# Quotation execution

@joy_word(name="i", params=1, doc="[P] -> ...")
def i_combinator(ctx: ExecutionContext) -> None:
    """Execute quotation."""
    quot = ctx.stack.pop()
    if quot.type != JoyType.QUOTATION:
        raise JoyTypeError("i", "QUOTATION", quot.type.name)
    ctx.evaluator.execute(quot.value)


# I/O (minimal for Phase 1)

@joy_word(name=".", params=1, doc="X ->")
def print_top(ctx: ExecutionContext) -> None:
    """Pop and print top of stack."""
    top = ctx.stack.pop()
    print(repr(top))


@joy_word(name="newline", params=0, doc="->")
def newline(ctx: ExecutionContext) -> None:
    """Print a newline."""
    print()


# ============================================================================
# Phase 2: Basic Primitives
# ============================================================================

# ----------------------------------------------------------------------------
# Additional Stack Operations
# ----------------------------------------------------------------------------


@joy_word(name="over", params=2, doc="X Y -> X Y X")
def over(ctx: ExecutionContext) -> None:
    """Copy second item to top."""
    second = ctx.stack.peek(1)
    ctx.stack.push_value(second)


@joy_word(name="rotate", params=3, doc="X Y Z -> Y Z X")
def rotate(ctx: ExecutionContext) -> None:
    """Rotate top three items: X Y Z -> Y Z X."""
    z, y, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(y)
    ctx.stack.push_value(z)
    ctx.stack.push_value(x)


@joy_word(name="rollup", params=3, doc="X Y Z -> Z X Y")
def rollup(ctx: ExecutionContext) -> None:
    """Roll up top three items: X Y Z -> Z X Y."""
    z, y, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(z)
    ctx.stack.push_value(x)
    ctx.stack.push_value(y)


@joy_word(name="rolldown", params=3, doc="X Y Z -> Y Z X")
def rolldown(ctx: ExecutionContext) -> None:
    """Roll down top three items (same as rotate)."""
    z, y, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(y)
    ctx.stack.push_value(z)
    ctx.stack.push_value(x)


@joy_word(name="dupd", params=2, doc="X Y -> X X Y")
def dupd(ctx: ExecutionContext) -> None:
    """Duplicate second item."""
    y, x = ctx.stack.pop_n(2)
    ctx.stack.push_value(x)
    ctx.stack.push_value(x)
    ctx.stack.push_value(y)


@joy_word(name="popd", params=2, doc="X Y -> Y")
def popd(ctx: ExecutionContext) -> None:
    """Pop second item."""
    y, _ = ctx.stack.pop_n(2)
    ctx.stack.push_value(y)


@joy_word(name="swapd", params=3, doc="X Y Z -> Y X Z")
def swapd(ctx: ExecutionContext) -> None:
    """Swap second and third items."""
    z, y, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(y)
    ctx.stack.push_value(x)
    ctx.stack.push_value(z)


@joy_word(name="choice", params=3, doc="B T F -> X")
def choice(ctx: ExecutionContext) -> None:
    """If B is true, push T, else push F."""
    f, t, b = ctx.stack.pop_n(3)
    if b.is_truthy():
        ctx.stack.push_value(t)
    else:
        ctx.stack.push_value(f)


# ----------------------------------------------------------------------------
# Arithmetic Operations
# ----------------------------------------------------------------------------


def _numeric_value(v: JoyValue) -> int | float:
    """Extract numeric value, converting if needed."""
    if v.type == JoyType.INTEGER:
        return v.value
    elif v.type == JoyType.FLOAT:
        return v.value
    elif v.type == JoyType.CHAR:
        return ord(v.value)
    elif v.type == JoyType.BOOLEAN:
        return 1 if v.value else 0
    else:
        raise JoyTypeError("arithmetic", "numeric", v.type.name)


def _make_numeric(value: int | float) -> JoyValue:
    """Create JoyValue from numeric result, preserving int when possible."""
    if isinstance(value, float) and value.is_integer():
        return JoyValue.integer(int(value))
    elif isinstance(value, float):
        return JoyValue.floating(value)
    else:
        return JoyValue.integer(value)


@joy_word(name="+", params=2, doc="N1 N2 -> N3")
def add(ctx: ExecutionContext) -> None:
    """Add two numbers."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) + _numeric_value(b)
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="-", params=2, doc="N1 N2 -> N3")
def sub(ctx: ExecutionContext) -> None:
    """Subtract: N1 - N2."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) - _numeric_value(b)
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="*", params=2, doc="N1 N2 -> N3")
def mul(ctx: ExecutionContext) -> None:
    """Multiply two numbers."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) * _numeric_value(b)
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="/", params=2, doc="N1 N2 -> N3")
def div(ctx: ExecutionContext) -> None:
    """Divide: N1 / N2. Integer division for integers."""
    b, a = ctx.stack.pop_n(2)
    bv = _numeric_value(b)
    if bv == 0:
        raise JoyDivisionByZero("/")
    av = _numeric_value(a)
    # Integer division if both are integers
    if isinstance(av, int) and isinstance(bv, int):
        result = av // bv
    else:
        result = av / bv
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="rem", params=2, doc="N1 N2 -> N3")
def rem(ctx: ExecutionContext) -> None:
    """Remainder: N1 % N2."""
    b, a = ctx.stack.pop_n(2)
    bv = _numeric_value(b)
    if bv == 0:
        raise JoyDivisionByZero("rem")
    result = _numeric_value(a) % bv
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="div", params=2, doc="N1 N2 -> Q R")
def divmod_word(ctx: ExecutionContext) -> None:
    """Integer division with remainder: push quotient then remainder."""
    b, a = ctx.stack.pop_n(2)
    bv = _numeric_value(b)
    if bv == 0:
        raise JoyDivisionByZero("div")
    av = _numeric_value(a)
    q = int(av // bv)
    r = av % bv
    ctx.stack.push_value(_make_numeric(q))
    ctx.stack.push_value(_make_numeric(r))


@joy_word(name="abs", params=1, doc="N -> N")
def abs_word(ctx: ExecutionContext) -> None:
    """Absolute value."""
    a = ctx.stack.pop()
    result = abs(_numeric_value(a))
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="neg", params=1, doc="N -> N")
def neg(ctx: ExecutionContext) -> None:
    """Negate: -N."""
    a = ctx.stack.pop()
    result = -_numeric_value(a)
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="sign", params=1, doc="N -> I")
def sign(ctx: ExecutionContext) -> None:
    """Sign: -1, 0, or 1."""
    a = ctx.stack.pop()
    v = _numeric_value(a)
    if v < 0:
        result = -1
    elif v > 0:
        result = 1
    else:
        result = 0
    ctx.stack.push_value(JoyValue.integer(result))


@joy_word(name="succ", params=1, doc="N -> N")
def succ(ctx: ExecutionContext) -> None:
    """Successor: N + 1."""
    a = ctx.stack.pop()
    result = _numeric_value(a) + 1
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="pred", params=1, doc="N -> N")
def pred(ctx: ExecutionContext) -> None:
    """Predecessor: N - 1."""
    a = ctx.stack.pop()
    result = _numeric_value(a) - 1
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="max", params=2, doc="N1 N2 -> N")
def max_word(ctx: ExecutionContext) -> None:
    """Maximum of two numbers."""
    b, a = ctx.stack.pop_n(2)
    av, bv = _numeric_value(a), _numeric_value(b)
    result = av if av >= bv else bv
    ctx.stack.push_value(_make_numeric(result))


@joy_word(name="min", params=2, doc="N1 N2 -> N")
def min_word(ctx: ExecutionContext) -> None:
    """Minimum of two numbers."""
    b, a = ctx.stack.pop_n(2)
    av, bv = _numeric_value(a), _numeric_value(b)
    result = av if av <= bv else bv
    ctx.stack.push_value(_make_numeric(result))


# ----------------------------------------------------------------------------
# Comparison Operations
# ----------------------------------------------------------------------------


@joy_word(name="<", params=2, doc="X Y -> B")
def lt(ctx: ExecutionContext) -> None:
    """Less than."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) < _numeric_value(b)
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name=">", params=2, doc="X Y -> B")
def gt(ctx: ExecutionContext) -> None:
    """Greater than."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) > _numeric_value(b)
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name="<=", params=2, doc="X Y -> B")
def le(ctx: ExecutionContext) -> None:
    """Less than or equal."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) <= _numeric_value(b)
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name=">=", params=2, doc="X Y -> B")
def ge(ctx: ExecutionContext) -> None:
    """Greater than or equal."""
    b, a = ctx.stack.pop_n(2)
    result = _numeric_value(a) >= _numeric_value(b)
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name="=", params=2, doc="X Y -> B")
def eq(ctx: ExecutionContext) -> None:
    """Equal (structural equality)."""
    b, a = ctx.stack.pop_n(2)
    # For numeric types, compare values
    if a.is_numeric() and b.is_numeric():
        result = _numeric_value(a) == _numeric_value(b)
    else:
        # Structural equality
        result = a == b
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name="!=", params=2, doc="X Y -> B")
def ne(ctx: ExecutionContext) -> None:
    """Not equal."""
    b, a = ctx.stack.pop_n(2)
    if a.is_numeric() and b.is_numeric():
        result = _numeric_value(a) != _numeric_value(b)
    else:
        result = a != b
    ctx.stack.push_value(JoyValue.boolean(result))


# ----------------------------------------------------------------------------
# Boolean Operations
# ----------------------------------------------------------------------------


@joy_word(name="and", params=2, doc="B1 B2 -> B")
def and_word(ctx: ExecutionContext) -> None:
    """Logical and."""
    b, a = ctx.stack.pop_n(2)
    result = a.is_truthy() and b.is_truthy()
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name="or", params=2, doc="B1 B2 -> B")
def or_word(ctx: ExecutionContext) -> None:
    """Logical or."""
    b, a = ctx.stack.pop_n(2)
    result = a.is_truthy() or b.is_truthy()
    ctx.stack.push_value(JoyValue.boolean(result))


@joy_word(name="not", params=1, doc="B -> B")
def not_word(ctx: ExecutionContext) -> None:
    """Logical not."""
    a = ctx.stack.pop()
    result = not a.is_truthy()
    ctx.stack.push_value(JoyValue.boolean(result))


# ----------------------------------------------------------------------------
# List/Aggregate Operations
# ----------------------------------------------------------------------------


def _get_aggregate(v: JoyValue, op: str) -> tuple:
    """Extract aggregate contents as tuple."""
    if v.type == JoyType.LIST:
        return v.value
    elif v.type == JoyType.QUOTATION:
        return v.value.terms
    elif v.type == JoyType.STRING:
        # String as tuple of chars
        return tuple(JoyValue.char(c) for c in v.value)
    elif v.type == JoyType.SET:
        return tuple(JoyValue.integer(x) for x in sorted(v.value))
    else:
        raise JoyTypeError(op, "aggregate", v.type.name)


def _make_aggregate(items: tuple, original_type: JoyType) -> JoyValue:
    """Create aggregate from items, matching original type where possible."""
    if original_type == JoyType.STRING:
        # Try to convert back to string
        try:
            chars = "".join(v.value for v in items if v.type == JoyType.CHAR)
            return JoyValue.string(chars)
        except (AttributeError, TypeError):
            return JoyValue.list(items)
    elif original_type == JoyType.SET:
        # Convert back to set
        try:
            members = frozenset(v.value for v in items if v.type == JoyType.INTEGER)
            return JoyValue.joy_set(members)
        except Exception:
            return JoyValue.list(items)
    else:
        return JoyValue.list(items)


@joy_word(name="cons", params=2, doc="X A -> A")
def cons(ctx: ExecutionContext) -> None:
    """Prepend X to aggregate A."""
    agg, x = ctx.stack.pop_n(2)
    items = _get_aggregate(agg, "cons")
    new_items = (x,) + items
    ctx.stack.push_value(_make_aggregate(new_items, agg.type))


@joy_word(name="swons", params=2, doc="A X -> A")
def swons(ctx: ExecutionContext) -> None:
    """Swap and cons: A X -> [X | A]."""
    x, agg = ctx.stack.pop_n(2)
    items = _get_aggregate(agg, "swons")
    new_items = (x,) + items
    ctx.stack.push_value(_make_aggregate(new_items, agg.type))


@joy_word(name="first", params=1, doc="A -> X")
def first(ctx: ExecutionContext) -> None:
    """Get first element of aggregate."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "first")
    if not items:
        raise JoyEmptyAggregate("first")
    ctx.stack.push_value(items[0])


@joy_word(name="rest", params=1, doc="A -> A")
def rest(ctx: ExecutionContext) -> None:
    """Get aggregate without first element."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "rest")
    if not items:
        raise JoyEmptyAggregate("rest")
    new_items = items[1:]
    ctx.stack.push_value(_make_aggregate(new_items, agg.type))


@joy_word(name="uncons", params=1, doc="A -> X A")
def uncons(ctx: ExecutionContext) -> None:
    """Split aggregate into first and rest."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "uncons")
    if not items:
        raise JoyEmptyAggregate("uncons")
    ctx.stack.push_value(items[0])
    ctx.stack.push_value(_make_aggregate(items[1:], agg.type))


@joy_word(name="unswons", params=1, doc="A -> A X")
def unswons(ctx: ExecutionContext) -> None:
    """Split aggregate into rest and first."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "unswons")
    if not items:
        raise JoyEmptyAggregate("unswons")
    ctx.stack.push_value(_make_aggregate(items[1:], agg.type))
    ctx.stack.push_value(items[0])


@joy_word(name="null", params=1, doc="A -> B")
def null(ctx: ExecutionContext) -> None:
    """Test if aggregate is empty."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "null")
    ctx.stack.push_value(JoyValue.boolean(len(items) == 0))


@joy_word(name="small", params=1, doc="A -> B")
def small(ctx: ExecutionContext) -> None:
    """Test if aggregate has 0 or 1 elements."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "small")
    ctx.stack.push_value(JoyValue.boolean(len(items) <= 1))


@joy_word(name="size", params=1, doc="A -> N")
def size(ctx: ExecutionContext) -> None:
    """Get size of aggregate."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "size")
    ctx.stack.push_value(JoyValue.integer(len(items)))


@joy_word(name="concat", params=2, doc="A1 A2 -> A")
def concat(ctx: ExecutionContext) -> None:
    """Concatenate two aggregates."""
    b, a = ctx.stack.pop_n(2)
    items_a = _get_aggregate(a, "concat")
    items_b = _get_aggregate(b, "concat")
    new_items = items_a + items_b
    ctx.stack.push_value(_make_aggregate(new_items, a.type))


@joy_word(name="reverse", params=1, doc="A -> A")
def reverse(ctx: ExecutionContext) -> None:
    """Reverse an aggregate."""
    agg = ctx.stack.pop()
    items = _get_aggregate(agg, "reverse")
    new_items = items[::-1]
    ctx.stack.push_value(_make_aggregate(new_items, agg.type))


@joy_word(name="at", params=2, doc="A N -> X")
def at(ctx: ExecutionContext) -> None:
    """Get element at index N from aggregate A."""
    n, agg = ctx.stack.pop_n(2)
    if n.type != JoyType.INTEGER:
        raise JoyTypeError("at", "INTEGER", n.type.name)
    items = _get_aggregate(agg, "at")
    idx = n.value
    if idx < 0 or idx >= len(items):
        raise JoyEmptyAggregate(f"at: index {idx} out of bounds")
    ctx.stack.push_value(items[idx])


@joy_word(name="of", params=2, doc="N A -> X")
def of(ctx: ExecutionContext) -> None:
    """Get element at index N from aggregate A (N A -> X, reverse of at)."""
    agg, n = ctx.stack.pop_n(2)
    if n.type != JoyType.INTEGER:
        raise JoyTypeError("of", "INTEGER", n.type.name)
    items = _get_aggregate(agg, "of")
    idx = n.value
    if idx < 0 or idx >= len(items):
        raise JoyEmptyAggregate(f"of: index {idx} out of bounds")
    ctx.stack.push_value(items[idx])


# ----------------------------------------------------------------------------
# Type Predicates
# ----------------------------------------------------------------------------


@joy_word(name="integer", params=1, doc="X -> B")
def is_integer(ctx: ExecutionContext) -> None:
    """Test if X is an integer."""
    x = ctx.stack.pop()
    ctx.stack.push_value(JoyValue.boolean(x.type == JoyType.INTEGER))


@joy_word(name="float", params=1, doc="X -> B")
def is_float(ctx: ExecutionContext) -> None:
    """Test if X is a float."""
    x = ctx.stack.pop()
    ctx.stack.push_value(JoyValue.boolean(x.type == JoyType.FLOAT))


@joy_word(name="char", params=1, doc="X -> B")
def is_char(ctx: ExecutionContext) -> None:
    """Test if X is a character."""
    x = ctx.stack.pop()
    ctx.stack.push_value(JoyValue.boolean(x.type == JoyType.CHAR))


@joy_word(name="string", params=1, doc="X -> B")
def is_string(ctx: ExecutionContext) -> None:
    """Test if X is a string."""
    x = ctx.stack.pop()
    ctx.stack.push_value(JoyValue.boolean(x.type == JoyType.STRING))


@joy_word(name="list", params=1, doc="X -> B")
def is_list(ctx: ExecutionContext) -> None:
    """Test if X is a list."""
    x = ctx.stack.pop()
    ctx.stack.push_value(JoyValue.boolean(x.type == JoyType.LIST))


@joy_word(name="logical", params=1, doc="X -> B")
def is_logical(ctx: ExecutionContext) -> None:
    """Test if X is a boolean."""
    x = ctx.stack.pop()
    ctx.stack.push_value(JoyValue.boolean(x.type == JoyType.BOOLEAN))
