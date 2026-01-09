"""
pyjoy.stack - Stack implementation and execution context.

The Joy stack is the central data structure for evaluation.
All operations manipulate values on the stack.

Supports two modes:
- Strict mode (JoyStack): All values wrapped in JoyValue
- Pythonic mode (PythonStack): Any Python object allowed
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Protocol, Tuple, Union, runtime_checkable

from pyjoy.errors import JoyStackUnderflow
from pyjoy.types import JoyValue, python_to_joy

if TYPE_CHECKING:
    from pyjoy.evaluator import Evaluator


@runtime_checkable
class StackProtocol(Protocol):
    """
    Protocol defining the stack interface.

    Both JoyStack (strict mode) and PythonStack (pythonic mode)
    implement this protocol.
    """

    def push(self, value: Any) -> None:
        """Push a value onto the stack."""
        ...

    def push_value(self, value: Any) -> None:
        """Push a value directly (no conversion in pythonic mode)."""
        ...

    def pop(self) -> Any:
        """Pop and return top of stack."""
        ...

    def peek(self, depth: int = 0) -> Any:
        """Peek at item at given depth without removing."""
        ...

    def pop_n(self, n: int) -> Tuple[Any, ...]:
        """Pop n items, returning tuple with TOS first."""
        ...

    def push_many(self, *values: Any) -> None:
        """Push multiple values."""
        ...

    @property
    def depth(self) -> int:
        """Current stack depth."""
        ...

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        ...

    def clear(self) -> None:
        """Clear all items."""
        ...

    def copy(self) -> "StackProtocol":
        """Create a shallow copy."""
        ...

    def items(self) -> List[Any]:
        """Return copy of items (bottom to top)."""
        ...


class JoyStack:
    """
    Joy evaluation stack.

    Uses a Python list internally but provides Joy-like interface.
    Stack grows upward: index -1 is TOS (top of stack).
    All values on the stack are JoyValue instances.
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: List[JoyValue] = []

    def push(self, value: Any) -> None:
        """
        Push value onto stack, auto-converting to JoyValue.

        Args:
            value: Any Python value (will be converted to JoyValue)
        """
        self._items.append(python_to_joy(value))

    def push_value(self, value: JoyValue) -> None:
        """
        Push a JoyValue directly onto stack (no conversion).

        Args:
            value: JoyValue to push
        """
        self._items.append(value)

    def pop(self) -> JoyValue:
        """
        Pop and return top of stack.

        Returns:
            The top JoyValue

        Raises:
            JoyStackUnderflow: If stack is empty
        """
        if not self._items:
            raise JoyStackUnderflow("pop", 1, 0)
        return self._items.pop()

    def peek(self, depth: int = 0) -> JoyValue:
        """
        Peek at stack item at given depth without removing.

        Args:
            depth: 0 = TOS, 1 = second item, etc.

        Returns:
            JoyValue at the specified depth

        Raises:
            JoyStackUnderflow: If depth exceeds stack size
        """
        if depth >= len(self._items):
            raise JoyStackUnderflow("peek", depth + 1, len(self._items))
        return self._items[-(depth + 1)]

    def pop_n(self, n: int) -> Tuple[JoyValue, ...]:
        """
        Pop n items from stack.

        Args:
            n: Number of items to pop

        Returns:
            Tuple of JoyValues, TOS first

        Raises:
            JoyStackUnderflow: If stack has fewer than n items
        """
        if n > len(self._items):
            raise JoyStackUnderflow("pop_n", n, len(self._items))
        if n == 0:
            return ()
        result = tuple(self._items[-n:])
        self._items = self._items[:-n]
        return result[::-1]  # Reverse so TOS is first

    def push_many(self, *values: Any) -> None:
        """
        Push multiple values (first arg pushed first).

        Args:
            values: Values to push (each converted to JoyValue)
        """
        for v in values:
            self.push(v)

    @property
    def depth(self) -> int:
        """Current stack depth."""
        return len(self._items)

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._items) == 0

    def clear(self) -> None:
        """Clear all items from stack."""
        self._items.clear()

    def copy(self) -> JoyStack:
        """Create a shallow copy for state preservation."""
        new_stack = JoyStack()
        new_stack._items = self._items.copy()
        return new_stack

    def items(self) -> List[JoyValue]:
        """Return a copy of the stack items (bottom to top)."""
        return self._items.copy()

    def __repr__(self) -> str:
        return f"Stack({[repr(v) for v in self._items]})"

    def __len__(self) -> int:
        return len(self._items)


class PythonStack:
    """
    Pythonic stack for non-strict mode.

    Unlike JoyStack, this stack accepts any Python object directly
    without wrapping in JoyValue. This enables seamless Python interop.

    Used when Evaluator is initialized with strict=False.
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: List[Any] = []

    def push(self, value: Any) -> None:
        """
        Push value onto stack (no conversion).

        Args:
            value: Any Python value
        """
        self._items.append(value)

    def push_value(self, value: Any) -> None:
        """
        Push value directly onto stack (same as push in pythonic mode).

        Args:
            value: Any value to push
        """
        self._items.append(value)

    def pop(self) -> Any:
        """
        Pop and return top of stack.

        Returns:
            The top value

        Raises:
            JoyStackUnderflow: If stack is empty
        """
        if not self._items:
            raise JoyStackUnderflow("pop", 1, 0)
        return self._items.pop()

    def peek(self, depth: int = 0) -> Any:
        """
        Peek at stack item at given depth without removing.

        Args:
            depth: 0 = TOS, 1 = second item, etc.

        Returns:
            Value at the specified depth

        Raises:
            JoyStackUnderflow: If depth exceeds stack size
        """
        if depth >= len(self._items):
            raise JoyStackUnderflow("peek", depth + 1, len(self._items))
        return self._items[-(depth + 1)]

    def pop_n(self, n: int) -> Tuple[Any, ...]:
        """
        Pop n items from stack.

        Args:
            n: Number of items to pop

        Returns:
            Tuple of values, TOS first

        Raises:
            JoyStackUnderflow: If stack has fewer than n items
        """
        if n > len(self._items):
            raise JoyStackUnderflow("pop_n", n, len(self._items))
        if n == 0:
            return ()
        result = tuple(self._items[-n:])
        self._items = self._items[:-n]
        return result[::-1]  # Reverse so TOS is first

    def push_many(self, *values: Any) -> None:
        """
        Push multiple values (first arg pushed first).

        Args:
            values: Values to push
        """
        for v in values:
            self.push(v)

    @property
    def depth(self) -> int:
        """Current stack depth."""
        return len(self._items)

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._items) == 0

    def clear(self) -> None:
        """Clear all items from stack."""
        self._items.clear()

    def copy(self) -> PythonStack:
        """Create a shallow copy for state preservation."""
        new_stack = PythonStack()
        new_stack._items = self._items.copy()
        return new_stack

    def items(self) -> List[Any]:
        """Return a copy of the stack items (bottom to top)."""
        return self._items.copy()

    def __repr__(self) -> str:
        return f"PythonStack({self._items})"

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> Any:
        """Support indexing: stack[-1] for top, stack[0] for bottom."""
        return self._items[index]

    def __iter__(self):
        """Support iteration over stack items."""
        return iter(self._items)


# Type alias for either stack type
AnyStack = Union[JoyStack, PythonStack]


class ExecutionContext:
    """
    Manages execution state including saved stacks.

    This is equivalent to the C implementation's env structure,
    with dump stacks for state preservation in conditionals
    and combinators.

    Supports two modes:
    - strict=True (default): Uses JoyStack, all values are JoyValue
    - strict=False: Uses PythonStack, any Python object allowed
    """

    __slots__ = ("stack", "_saved_states", "_evaluator", "_strict")

    def __init__(self, strict: bool = True) -> None:
        self._strict = strict
        self.stack: AnyStack = JoyStack() if strict else PythonStack()
        self._saved_states: List[List[Any]] = []
        self._evaluator: Evaluator | None = None

    @property
    def strict(self) -> bool:
        """Whether this context is in strict mode."""
        return self._strict

    def save_stack(self) -> int:
        """
        Save current stack state.

        Returns:
            State ID for later restoration

        This is equivalent to the SAVESTACK macro in C.
        """
        self._saved_states.append(self.stack._items.copy())
        return len(self._saved_states) - 1

    def restore_stack(self, state_id: int) -> None:
        """
        Restore stack to a saved state.

        Args:
            state_id: ID returned by save_stack()
        """
        self.stack._items = self._saved_states[state_id].copy()

    def pop_saved(self) -> None:
        """
        Pop most recent saved state.

        Equivalent to POP(env->dump) in C.
        """
        if self._saved_states:
            self._saved_states.pop()

    def get_saved(self, state_id: int, depth: int) -> Any:
        """
        Get item from a saved state.

        Args:
            state_id: ID of saved state
            depth: Depth from top (0 = top)

        Returns:
            Value at specified position in saved state
            (JoyValue in strict mode, any object in pythonic mode)
        """
        saved = self._saved_states[state_id]
        return saved[-(depth + 1)]

    def set_evaluator(self, evaluator: Evaluator) -> None:
        """Set the evaluator reference for combinator execution."""
        self._evaluator = evaluator

    @property
    def evaluator(self) -> Evaluator:
        """Get the evaluator reference."""
        if self._evaluator is None:
            raise RuntimeError("Evaluator not set on ExecutionContext")
        return self._evaluator
