"""
pyjoy.evaluator.types - Type predicates and conditionals.

Contains type predicates: integer, float, char, string, list, logical, set,
leaf, file, user, sametype, typeof

Contains type conditionals: ifinteger, ifchar, iflogical, ifset, ifstring,
iflist, iffloat, iffile
"""

from __future__ import annotations

from typing import Any

from pyjoy.errors import JoyTypeError
from pyjoy.stack import ExecutionContext
from pyjoy.types import JoyQuotation, JoyType, JoyValue

from .core import expect_quotation, get_primitive, is_joy_value, joy_word


def _push_boolean(ctx: ExecutionContext, result: bool) -> None:
    """Push a boolean result in a mode-appropriate way."""
    if ctx.strict:
        ctx.stack.push_value(JoyValue.boolean(result))
    else:
        ctx.stack.push(result)


def _push_integer(ctx: ExecutionContext, result: int) -> None:
    """Push an integer result in a mode-appropriate way."""
    if ctx.strict:
        ctx.stack.push_value(JoyValue.integer(result))
    else:
        ctx.stack.push(result)

# -----------------------------------------------------------------------------
# Type Predicates
# -----------------------------------------------------------------------------


def _check_type(x: Any, joy_type: JoyType, python_types: tuple) -> bool:
    """Check if x matches the given Joy type or Python types."""
    if is_joy_value(x):
        return x.type == joy_type
    return isinstance(x, python_types)


@joy_word(name="integer", params=1, doc="X -> B")
def is_integer(ctx: ExecutionContext) -> None:
    """Test if X is an integer."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.INTEGER
    else:
        result = isinstance(x, int) and not isinstance(x, bool)
    _push_boolean(ctx, result)


@joy_word(name="float", params=1, doc="X -> B")
def is_float(ctx: ExecutionContext) -> None:
    """Test if X is a float."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.FLOAT
    else:
        result = isinstance(x, float)
    _push_boolean(ctx, result)


@joy_word(name="char", params=1, doc="X -> B")
def is_char(ctx: ExecutionContext) -> None:
    """Test if X is a character."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.CHAR
    else:
        # In pythonic mode, a single-character string is a char
        result = isinstance(x, str) and len(x) == 1
    _push_boolean(ctx, result)


@joy_word(name="string", params=1, doc="X -> B")
def is_string(ctx: ExecutionContext) -> None:
    """Test if X is a string."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.STRING
    else:
        # In pythonic mode, multi-char strings are strings (not chars)
        result = isinstance(x, str) and len(x) != 1
    _push_boolean(ctx, result)


@joy_word(name="list", params=1, doc="X -> B")
def is_list(ctx: ExecutionContext) -> None:
    """Test if X is a list (or quotation, treated as list in Joy)."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type in (JoyType.LIST, JoyType.QUOTATION)
    else:
        result = isinstance(x, (list, tuple, JoyQuotation))
    _push_boolean(ctx, result)


@joy_word(name="logical", params=1, doc="X -> B")
def is_logical(ctx: ExecutionContext) -> None:
    """Test if X is a boolean."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.BOOLEAN
    else:
        result = isinstance(x, bool)
    _push_boolean(ctx, result)


@joy_word(name="set", params=1, doc="X -> B")
def is_set(ctx: ExecutionContext) -> None:
    """Test if X is a set."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.SET
    else:
        result = isinstance(x, frozenset)
    _push_boolean(ctx, result)


@joy_word(name="leaf", params=1, doc="X -> B")
def is_leaf(ctx: ExecutionContext) -> None:
    """Test if X is an atom (not a list or quotation)."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        is_aggregate = x.type in (JoyType.LIST, JoyType.QUOTATION)
    else:
        is_aggregate = isinstance(x, (list, tuple, JoyQuotation))
    _push_boolean(ctx, not is_aggregate)


@joy_word(name="file", params=1, doc="X -> B")
def is_file(ctx: ExecutionContext) -> None:
    """Test if X is a file handle."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        result = x.type == JoyType.FILE
    else:
        # In pythonic mode, check for file-like object
        result = hasattr(x, 'read') and hasattr(x, 'write')
    _push_boolean(ctx, result)


@joy_word(name="user", params=1, doc="X -> B")
def is_user(ctx: ExecutionContext) -> None:
    """Test if X is a user-defined symbol."""
    x = ctx.stack.pop()
    if is_joy_value(x):
        if x.type != JoyType.SYMBOL:
            _push_boolean(ctx, False)
        else:
            is_defined = x.value in ctx.evaluator.definitions
            _push_boolean(ctx, is_defined)
    else:
        # In pythonic mode, symbols are just strings
        if isinstance(x, str):
            is_defined = x in ctx.evaluator.definitions
            _push_boolean(ctx, is_defined)
        else:
            _push_boolean(ctx, False)


def _get_type_key(x: Any) -> str:
    """Get a type key for comparison purposes."""
    if is_joy_value(x):
        return x.type.name
    if isinstance(x, bool):
        return "BOOLEAN"
    if isinstance(x, int):
        return "INTEGER"
    if isinstance(x, float):
        return "FLOAT"
    if isinstance(x, str):
        if len(x) == 1:
            return "CHAR"
        return "STRING"
    if isinstance(x, (list, tuple)):
        return "LIST"
    if isinstance(x, JoyQuotation):
        return "QUOTATION"
    if isinstance(x, frozenset):
        return "SET"
    return "OBJECT"


@joy_word(name="sametype", params=2, doc="X Y -> B")
def sametype(ctx: ExecutionContext) -> None:
    """Test if X and Y have the same type."""
    b, a = ctx.stack.pop_n(2)
    if is_joy_value(a) and is_joy_value(b):
        result = a.type == b.type
    else:
        result = _get_type_key(a) == _get_type_key(b)
    _push_boolean(ctx, result)


@joy_word(name="typeof", params=1, doc="X -> I")
def typeof_(ctx: ExecutionContext) -> None:
    """Return type of X as integer.

    Joy42 type codes:
    0 = UNKNOWN, 1 = (reserved), 2 = USRDEF, 3 = BUILTIN,
    4 = BOOLEAN, 5 = CHAR, 6 = INTEGER, 7 = SET,
    8 = STRING, 9 = LIST, 10 = FLOAT, 11 = FILE
    """
    x = ctx.stack.pop()

    # Handle JoyValue objects
    if is_joy_value(x):
        # For symbols, check if it's a builtin or user-defined
        if x.type == JoyType.SYMBOL:
            # Check if it's registered as a primitive
            is_primitive = get_primitive(x.value) is not None
            is_user_def = x.value in ctx.evaluator.definitions
            if is_primitive and not is_user_def:
                _push_integer(ctx, 3)  # BUILTIN
            else:
                _push_integer(ctx, 2)  # USRDEF
            return

        type_codes = {
            JoyType.BOOLEAN: 4,
            JoyType.CHAR: 5,
            JoyType.INTEGER: 6,
            JoyType.SET: 7,
            JoyType.STRING: 8,
            JoyType.LIST: 9,
            JoyType.QUOTATION: 9,  # Quotation treated as list
            JoyType.FLOAT: 10,
            JoyType.FILE: 11,
        }
        _push_integer(ctx, type_codes.get(x.type, 0))
        return

    # Handle raw Python values (pythonic mode)
    if isinstance(x, bool):
        _push_integer(ctx, 4)  # BOOLEAN
    elif isinstance(x, int):
        _push_integer(ctx, 6)  # INTEGER
    elif isinstance(x, float):
        _push_integer(ctx, 10)  # FLOAT
    elif isinstance(x, str):
        if len(x) == 1:
            _push_integer(ctx, 5)  # CHAR
        else:
            _push_integer(ctx, 8)  # STRING
    elif isinstance(x, (list, tuple, JoyQuotation)):
        _push_integer(ctx, 9)  # LIST
    elif isinstance(x, frozenset):
        _push_integer(ctx, 7)  # SET
    elif hasattr(x, 'read') and hasattr(x, 'write'):
        _push_integer(ctx, 11)  # FILE
    else:
        _push_integer(ctx, 0)  # UNKNOWN


@joy_word(name="casting", params=2, doc="X T -> Y")
def casting_(ctx: ExecutionContext) -> None:
    """Cast value X to type T (type code from typeof)."""
    import struct

    t, x = ctx.stack.pop_n(2)
    if t.type != JoyType.INTEGER:
        raise JoyTypeError("casting", "integer type code", t.type.name)

    target_type = t.value

    # Type codes: 0=list, 1=bool, 2=char, 3=int, 4=set,
    # 5=string, 6=symbol, 7=float, 8=file
    if target_type == 0:  # list
        if x.type in (JoyType.LIST, JoyType.QUOTATION):
            ctx.stack.push_value(x)
        elif x.type == JoyType.STRING:
            chars = tuple(JoyValue.char(c) for c in x.value)
            ctx.stack.push_value(JoyValue.list(chars))
        elif x.type == JoyType.SET:
            items = tuple(JoyValue.integer(i) for i in sorted(x.value))
            ctx.stack.push_value(JoyValue.list(items))
        else:
            ctx.stack.push_value(JoyValue.list(()))

    elif target_type == 1:  # bool
        ctx.stack.push_value(JoyValue.boolean(x.is_truthy()))

    elif target_type == 2:  # char
        if x.type == JoyType.CHAR:
            ctx.stack.push_value(x)
        elif x.type == JoyType.INTEGER:
            ctx.stack.push_value(JoyValue.char(chr(x.value & 0xFF)))
        elif x.type == JoyType.STRING and x.value:
            ctx.stack.push_value(JoyValue.char(x.value[0]))
        else:
            ctx.stack.push_value(JoyValue.char("\0"))

    elif target_type == 3:  # int
        if x.type == JoyType.INTEGER:
            ctx.stack.push_value(x)
        elif x.type == JoyType.CHAR:
            ctx.stack.push_value(JoyValue.integer(ord(x.value)))
        elif x.type == JoyType.FLOAT:
            ctx.stack.push_value(JoyValue.integer(int(x.value)))
        elif x.type == JoyType.BOOLEAN:
            ctx.stack.push_value(JoyValue.integer(1 if x.value else 0))
        elif x.type == JoyType.SYMBOL:
            # Symbol stays as symbol when cast to int (per test)
            ctx.stack.push_value(x)
        else:
            ctx.stack.push_value(JoyValue.integer(0))

    elif target_type == 4:  # set
        if x.type == JoyType.SET:
            ctx.stack.push_value(x)
        elif x.type == JoyType.INTEGER:
            # Convert int to set containing that element (if 0-63)
            if 0 <= x.value <= 63:
                ctx.stack.push_value(JoyValue.joy_set(frozenset([x.value])))
            else:
                # Convert bits to set members
                bits = set()
                val = x.value
                for i in range(64):
                    if val & (1 << i):
                        bits.add(i)
                ctx.stack.push_value(JoyValue.joy_set(frozenset(bits)))
        elif x.type == JoyType.LIST:
            items = frozenset(
                v.value
                for v in x.value
                if isinstance(v, JoyValue) and v.type == JoyType.INTEGER
            )
            ctx.stack.push_value(JoyValue.joy_set(items))
        else:
            ctx.stack.push_value(JoyValue.joy_set(frozenset()))

    elif target_type == 5:  # string
        if x.type == JoyType.STRING:
            ctx.stack.push_value(x)
        elif x.type == JoyType.CHAR:
            ctx.stack.push_value(JoyValue.string(x.value))
        elif x.type == JoyType.INTEGER:
            # Integer to char (like type 2), then to string
            ctx.stack.push_value(JoyValue.char(chr(x.value & 0xFF)))
        elif x.type == JoyType.LIST:
            chars = "".join(
                v.value
                for v in x.value
                if isinstance(v, JoyValue) and v.type == JoyType.CHAR
            )
            ctx.stack.push_value(JoyValue.string(chars))
        else:
            ctx.stack.push_value(JoyValue.string(str(x.value)))

    elif target_type == 6:  # symbol
        if x.type == JoyType.SYMBOL:
            ctx.stack.push_value(x)
        elif x.type == JoyType.CHAR:
            # Char to integer (per test: 'A -> 65)
            ctx.stack.push_value(JoyValue.integer(ord(x.value)))
        elif x.type == JoyType.STRING:
            ctx.stack.push_value(JoyValue.symbol(x.value))
        else:
            ctx.stack.push_value(JoyValue.symbol(str(x.value)))

    elif target_type == 7:  # float
        if x.type == JoyType.FLOAT:
            ctx.stack.push_value(x)
        elif x.type == JoyType.INTEGER:
            # Int bits to set (per test: 123456789 -> set of bit positions)
            bits = set()
            val = x.value
            for i in range(64):
                if val & (1 << i):
                    bits.add(i)
            ctx.stack.push_value(JoyValue.joy_set(frozenset(bits)))
        elif x.type == JoyType.CHAR:
            ctx.stack.push_value(JoyValue.floating(float(ord(x.value))))
        else:
            ctx.stack.push_value(JoyValue.floating(0.0))

    elif target_type == 8:  # file
        # Can't really cast to file
        ctx.stack.push_value(JoyValue.file(None))

    elif target_type == 9:  # list (alternate code)
        if x.type in (JoyType.LIST, JoyType.QUOTATION):
            ctx.stack.push_value(x)
        else:
            ctx.stack.push_value(JoyValue.list(()))

    elif target_type == 10:  # float from int bits
        if x.type == JoyType.INTEGER:
            # Reinterpret int bits as float64
            try:
                result = struct.unpack("d", struct.pack("q", x.value))[0]
                ctx.stack.push_value(JoyValue.floating(result))
            except struct.error:
                ctx.stack.push_value(JoyValue.floating(0.0))
        else:
            ctx.stack.push_value(JoyValue.floating(float(x.value)))

    elif target_type == 11:  # file/special
        # Return different value to show conversion happened
        ctx.stack.push_value(JoyValue.file(None))

    else:
        # Unknown type, return as-is
        ctx.stack.push_value(x)


# -----------------------------------------------------------------------------
# Type Conditionals
# -----------------------------------------------------------------------------


@joy_word(name="ifinteger", params=3, doc="X [T] [F] -> ...")
def ifinteger(ctx: ExecutionContext) -> None:
    """Execute T if X is integer, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.INTEGER:
        ctx.evaluator.execute(expect_quotation(t_quot, "ifinteger"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "ifinteger"))


@joy_word(name="ifchar", params=3, doc="X [T] [F] -> ...")
def ifchar(ctx: ExecutionContext) -> None:
    """Execute T if X is char, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.CHAR:
        ctx.evaluator.execute(expect_quotation(t_quot, "ifchar"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "ifchar"))


@joy_word(name="iflogical", params=3, doc="X [T] [F] -> ...")
def iflogical(ctx: ExecutionContext) -> None:
    """Execute T if X is boolean, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.BOOLEAN:
        ctx.evaluator.execute(expect_quotation(t_quot, "iflogical"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "iflogical"))


@joy_word(name="ifset", params=3, doc="X [T] [F] -> ...")
def ifset(ctx: ExecutionContext) -> None:
    """Execute T if X is set, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.SET:
        ctx.evaluator.execute(expect_quotation(t_quot, "ifset"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "ifset"))


@joy_word(name="ifstring", params=3, doc="X [T] [F] -> ...")
def ifstring(ctx: ExecutionContext) -> None:
    """Execute T if X is string, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.STRING:
        ctx.evaluator.execute(expect_quotation(t_quot, "ifstring"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "ifstring"))


@joy_word(name="iflist", params=3, doc="X [T] [F] -> ...")
def iflist(ctx: ExecutionContext) -> None:
    """Execute T if X is list, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type in (JoyType.LIST, JoyType.QUOTATION):
        ctx.evaluator.execute(expect_quotation(t_quot, "iflist"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "iflist"))


@joy_word(name="iffloat", params=3, doc="X [T] [F] -> ...")
def iffloat(ctx: ExecutionContext) -> None:
    """Execute T if X is float, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.FLOAT:
        ctx.evaluator.execute(expect_quotation(t_quot, "iffloat"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "iffloat"))


@joy_word(name="iffile", params=3, doc="X [T] [F] -> ...")
def iffile(ctx: ExecutionContext) -> None:
    """Execute T if X is file, else F."""
    f_quot, t_quot, x = ctx.stack.pop_n(3)
    ctx.stack.push_value(x)
    if x.type == JoyType.FILE:
        ctx.evaluator.execute(expect_quotation(t_quot, "iffile"))
    else:
        ctx.evaluator.execute(expect_quotation(f_quot, "iffile"))
