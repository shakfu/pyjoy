"""
pyjoy.errors - Custom exception types for Joy interpreter.
"""


class JoyError(Exception):
    """Base class for all Joy errors."""

    pass


class JoyStackUnderflowError(JoyError):
    """Raised when a stack operation requires more items than available."""

    def __init__(self, operation: str, required: int, available: int):
        self.operation = operation
        self.required = required
        self.available = available
        super().__init__(
            f"{operation}: requires {required} items, stack has {available}"
        )


# Backwards compatibility alias
JoyStackUnderflow = JoyStackUnderflowError


class JoyTypeError(JoyError):
    """Raised when a value has an unexpected type."""

    def __init__(self, operation: str, expected: str, actual: str, position: int = 0):
        self.operation = operation
        self.expected = expected
        self.actual = actual
        self.position = position
        if position > 0:
            super().__init__(
                f"{operation}: argument {position} expected {expected}, got {actual}"
            )
        else:
            super().__init__(f"{operation}: expected {expected}, got {actual}")


class JoyUndefinedWordError(JoyError):
    """Raised when an undefined word is referenced."""

    def __init__(self, word: str):
        self.word = word
        super().__init__(f"Undefined word: {word}")


# Backwards compatibility alias
JoyUndefinedWord = JoyUndefinedWordError


class JoySyntaxError(JoyError):
    """Raised for syntax errors during parsing."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
        if line > 0:
            super().__init__(f"{message} at line {line}, column {column}")
        else:
            super().__init__(message)


class JoySetMemberError(JoyError):
    """Raised when a set member is outside the valid range [0, 63]."""

    def __init__(self, member: int):
        self.member = member
        super().__init__(f"Set member {member} out of valid range [0, 63]")


class JoyDivisionByZeroError(JoyError):
    """Raised when attempting to divide by zero."""

    def __init__(self, operation: str = "/"):
        self.operation = operation
        super().__init__(f"{operation}: division by zero")


# Backwards compatibility alias
JoyDivisionByZero = JoyDivisionByZeroError


class JoyEmptyAggregateError(JoyError):
    """Raised when an operation requires a non-empty aggregate."""

    def __init__(self, operation: str):
        self.operation = operation
        super().__init__(f"{operation}: empty aggregate")


# Backwards compatibility alias
JoyEmptyAggregate = JoyEmptyAggregateError
