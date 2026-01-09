"""
pyjoy.repl - Interactive Read-Eval-Print Loop for Joy.

Supports:
- Joy words and quotations (strict mode)
- Python expressions via `expr` or $(expr) (pythonic mode)
- Python statements via !stmt (pythonic mode)
- Multi-line Python function definitions (pythonic mode)
- Commands: .s, .c, .w, .help, .def, .import, .load
"""

from __future__ import annotations

import re
import traceback
from typing import List

from pyjoy.errors import JoyError
from pyjoy.evaluator import Evaluator, list_primitives


class REPL:
    """
    Interactive Joy REPL with optional Python integration.

    Commands:
        quit, exit   - Exit the REPL
        .s, .stack   - Show stack with types
        .c, .clear   - Clear the stack
        .w, .words   - List available words
        .w PATTERN   - List words matching pattern
        .h, .help    - Show help
        .help WORD   - Show help for specific word
        .def N [B]   - Define word N with body B (pythonic mode)
        .import M    - Import Python module M (pythonic mode)
        .load F      - Load Joy file F
    """

    PROMPT = "> "
    CONTINUATION_PROMPT = "... "
    BANNER_STRICT = """\
PyJoy - Joy Programming Language Interpreter
Type 'quit' to exit, '.help' for commands.
"""
    BANNER_PYTHONIC = """\
PyJoy - Joy Programming Language Interpreter (Pythonic Mode)
Python interop enabled: `expr`, $(expr), !stmt
Type 'quit' to exit, '.help' for commands.
"""

    def __init__(self, strict: bool = True, debug: bool = False) -> None:
        self.strict = strict
        self.debug = debug
        self.evaluator = Evaluator(strict=strict)
        self.running = True
        self.pending_lines: List[str] = []

    def run(self) -> None:
        """Run the interactive REPL."""
        print(self.BANNER_STRICT if self.strict else self.BANNER_PYTHONIC)

        while self.running:
            try:
                prompt = self.CONTINUATION_PROMPT if self.pending_lines else self.PROMPT
                line = input(prompt)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'quit' to exit.")
                self.pending_lines = []
                continue

            self._process_line(line)

    def _process_line(self, line: str) -> None:
        """Process a single input line."""
        stripped = line.strip()

        # Handle quit (not in multi-line mode)
        if stripped in ("quit", "exit") and not self.pending_lines:
            self.running = False
            return

        # Handle empty line in pending block (finishes the block)
        if not stripped and self.pending_lines:
            self._finish_python_block()
            return

        # In pythonic mode, check for multi-line Python blocks
        if not self.strict and self._handle_python_block(line):
            return

        # Handle REPL commands (only when not in multi-line mode)
        if not self.pending_lines:
            if stripped in (".s", ".stack"):
                self._show_stack()
                return

            if stripped in (".c", ".clear"):
                self.evaluator.stack.clear()
                print("Stack cleared.")
                return

            if stripped in (".w", ".words"):
                self._show_words()
                return

            if stripped.startswith(".w "):
                self._show_words(stripped[3:].strip())
                return

            if stripped.startswith(".words "):
                self._show_words(stripped[7:].strip())
                return

            if stripped in (".h", ".help"):
                self._show_help()
                return

            if stripped.startswith(".help "):
                self._show_word_help(stripped[6:].strip())
                return

            if stripped.startswith(".def "):
                self._define_word(stripped[5:])
                return

            if stripped.startswith(".import "):
                self._import_module(stripped[8:].strip())
                return

            if stripped.startswith(".load "):
                self._load_file(stripped[6:].strip())
                return

        if not stripped:
            return

        # Execute as Joy code
        try:
            self.evaluator.run(stripped)
            self._show_stack_brief()
        except JoyError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            if self.debug:
                traceback.print_exc()

    def _is_incomplete(self, code: str) -> bool:
        """Check if Python code is incomplete (needs more lines)."""
        try:
            compile(code, "<input>", "exec")
            return False
        except SyntaxError as e:
            msg = str(e)
            return "unexpected EOF" in msg or "EOF while scanning" in msg

    def _handle_python_block(self, line: str) -> bool:
        """
        Handle multi-line Python blocks (def, class, etc.)
        Returns True if line was handled as Python block.
        """
        block_starters = (
            "def ",
            "class ",
            "if ",
            "for ",
            "while ",
            "with ",
            "try:",
            "async ",
            "@",
        )
        is_block_start = any(line.lstrip().startswith(s) for s in block_starters)

        if self.pending_lines or is_block_start:
            self.pending_lines.append(line)
            code = "\n".join(self.pending_lines)

            if self._is_incomplete(code):
                return True  # Need more lines

            # Execute complete block
            self._finish_python_block()
            return True

        return False

    def _finish_python_block(self) -> None:
        """Execute the accumulated Python block."""
        if not self.pending_lines:
            return

        code = "\n".join(self.pending_lines)
        self.pending_lines = []

        try:
            self.evaluator._python_exec(code)
            print("  OK")
        except Exception as e:
            print(f"  Error: {e}")
            if self.debug:
                traceback.print_exc()

    def _define_word(self, defn: str) -> None:
        """Define new word: .def name [body]"""
        if self.strict:
            print("  Error: .def requires pythonic mode (strict=False)")
            return

        match = re.match(r"(\w[\w\-\?]*)\s+\[(.+)\]", defn)
        if not match:
            print("  Usage: .def name [body]")
            return

        name, body = match.groups()

        # Define using Joy's DEFINE syntax
        try:
            self.evaluator.run(f"DEFINE {name} == {body}.")
            print(f"  Defined: {name}")
        except Exception as e:
            print(f"  Error: {e}")

    def _import_module(self, module: str) -> None:
        """Import a Python module."""
        if self.strict:
            print("  Error: .import requires pythonic mode (strict=False)")
            return

        try:
            self.evaluator._python_exec(f"import {module}")
            print(f"  Imported: {module}")
        except Exception as e:
            print(f"  Error: {e}")

    def _load_file(self, filename: str) -> None:
        """Load and execute a Joy file."""
        try:
            with open(filename) as f:
                source = f.read()
            self.evaluator.run(source)
            print(f"  Loaded: {filename}")
        except FileNotFoundError:
            print(f"  Error: file not found: {filename}")
        except Exception as e:
            print(f"  Error loading {filename}: {e}")
            if self.debug:
                traceback.print_exc()

    def _show_stack(self) -> None:
        """Show stack with type information."""
        stack = self.evaluator.stack
        if stack.is_empty():
            print("Stack: (empty)")
            return

        print("Stack (bottom to top):")
        for i, item in enumerate(stack.items()):
            if self.strict:
                print(f"  {i}: {item.type.name}: {item!r}")
            else:
                type_name = type(item).__name__
                repr_str = repr(item)
                if len(repr_str) > 60:
                    repr_str = repr_str[:57] + "..."
                print(f"  {i}: ({type_name}) {repr_str}")

    def _show_stack_brief(self) -> None:
        """Show brief stack representation."""
        stack = self.evaluator.stack
        if stack.is_empty():
            print("Stack: (empty)")
        else:
            items = " ".join(repr(v) for v in stack.items())
            if len(items) > 70:
                items = items[:67] + "..."
            print(f"Stack: {items}")

    def _show_words(self, pattern: str | None = None) -> None:
        """Show available words, optionally filtered by pattern."""
        primitives = list_primitives()
        definitions = sorted(self.evaluator.definitions.keys())

        all_words = primitives + definitions

        if pattern:
            all_words = [w for w in all_words if pattern in w]
            print(f"{len(all_words)} words matching '{pattern}':")
        else:
            print(f"Primitives ({len(primitives)}):")

        if not all_words:
            return

        # Print in columns
        cols = 6
        words_to_print = all_words if pattern else primitives
        for i in range(0, len(words_to_print), cols):
            row = words_to_print[i : i + cols]
            print("  " + "  ".join(f"{w:12}" for w in row))

        if not pattern and definitions:
            print(f"\nUser definitions ({len(definitions)}):")
            for i in range(0, len(definitions), cols):
                row = definitions[i : i + cols]
                print("  " + "  ".join(f"{w:12}" for w in row))

    def _show_word_help(self, word_name: str) -> None:
        """Show help for a specific word."""
        from pyjoy.evaluator.core import get_primitive

        primitive = get_primitive(word_name)

        if primitive is None and word_name not in self.evaluator.definitions:
            # Try to find similar words
            all_words = list_primitives() + list(self.evaluator.definitions.keys())
            similar = [w for w in all_words if word_name in w or w in word_name]
            print(f"Unknown word: {word_name}")
            if similar:
                print(f"Did you mean: {', '.join(sorted(similar)[:5])}")
            return

        print(f"\n  {word_name}")

        if primitive:
            doc = getattr(primitive, "joy_doc", None) or getattr(
                primitive, "__doc__", None
            )
            if doc:
                print(f"    {doc.strip()}")
            else:
                print("    (built-in, no documentation)")
        else:
            # User definition
            body = self.evaluator.definitions[word_name]
            print(f"    User-defined: {body}")

        print()

    def _show_help(self) -> None:
        """Show REPL help."""
        base_help = """\
REPL Commands:
  quit, exit   - Exit the REPL
  .s, .stack   - Show stack with types
  .c, .clear   - Clear the stack
  .w, .words   - List available words
  .w PATTERN   - List words matching pattern
  .h, .help    - Show this help
  .help WORD   - Show help for specific word
  .load FILE   - Load and execute Joy file

Joy Basics:
  42           - Push integer
  3.14         - Push float
  "hello"      - Push string
  'x'          - Push character
  true false   - Push booleans
  [1 2 3]      - Push quotation (list)
  {0 1 2}      - Push set

Stack Operations:
  dup          - Duplicate top
  pop          - Remove top
  swap         - Exchange top two
  i            - Execute quotation
  .            - Print and pop top
"""

        pythonic_help = """
Pythonic Mode Extensions:
  `expr`       - Evaluate Python expression, push result
  $(expr)      - Alternative Python expression syntax
  !stmt        - Execute Python statement (no push)
  .def N [B]   - Define word N with body B
  .import M    - Import Python module M

  Multi-line Python blocks (def, class, if, for, etc.)
  are automatically detected. End with empty line.

  Example:
    > def square(x):
    ...     return x * x
    ...
      OK
    > `square(5)`
    Stack: 25
"""

        print(base_help)
        if not self.strict:
            print(pythonic_help)


def run_repl(strict: bool = True, debug: bool = False) -> None:
    """Entry point for running the REPL."""
    repl = REPL(strict=strict, debug=debug)
    repl.run()
