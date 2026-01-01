# Changelog

## [Unreleased]

### Fixed
- `condlinrec`/`condnestrec`: Rewrote to match Joy reference implementation
  - Last clause is now treated as default (no B condition testing)
  - Both combinators share `condnestrecaux` implementation
  - Proper execution order: R1, recurse, R2, recurse, ...
- `not`: Now returns bitwise complement for SETs (was always returning boolean)
- `and`/`or`: Now perform set intersection/union for SET operands
- `cons`: Now supports adding elements to SETs
- `infra`: Now accepts both LIST and QUOTATION arguments

### Added
- `id`: Identity function (does nothing)
- `choice`: B T F -> X (if B then T else F)
- `xor`: Logical XOR / set symmetric difference
- `at`: A I -> X (get element at index I)
- `drop`: A N -> B (drop first N elements)
- `take`: A N -> B (take first N elements)
- `over`: X Y -> X Y X (copy second item to top)
- `dup2`: X Y -> X Y X Y (duplicate top two items)
- `newline`: Print newline (alias for `.`)
- `unswons`: A -> R F (rest and first, opposite of uncons)
- `of`: I A -> X (get element at index, reverse arg order of `at`)
- `compare`: A B -> I (compare values, return -1/0/1)
- `equal`: T U -> B (recursive structural equality test)
- `in`: X A -> B (membership test)
- `name`: sym -> "sym" (symbol/type to string)
- `intern`: "sym" -> sym (string to symbol)
- `body`: U -> [P] (get body of user-defined word)
- `maxint`: -> I (push maximum integer value)
- `setsize`: -> I (push set size, 64)

### Coverage
- C backend: 102/203 primitives (50%)

### Tests
- jp-nestrec.joy now runs to completion with all tests passing
- All 411 pytest tests pass
