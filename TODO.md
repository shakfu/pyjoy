# pyjoy C Backend - TODO

## Primitives Coverage

**Current: 145/203 (71%)** + 8 extensions

Run `uv run python scripts/check_c_coverage.py` for full report.

### Extensions (8)
- `.` / `newline` - Print newline
- `putln` - Put with newline
- `swoncat` - Swap then concat
- `condnestrec` - Conditional nested recursion
- `__settracegc` - Debug no-op
- `over` - X Y -> X Y X (copy second to top)
- `dup2` - X Y -> X Y X Y (duplicate top two)

---

## Remaining Primitives (58)

### Operand (5)

| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `conts` | `-> [[P] [Q] ..]` | Push continuation stack |
| `autoput` | `-> I` | Push autoput flag value |
| `undeferror` | `-> I` | Push undeferror flag value |
| `undefs` | `->` | Push list of undefined symbols |
| `echo` | `-> I` | Push echo flag value (0..3) |

### Operator (28)

#### Stack Variants
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `rollupd` | `X Y Z W -> Z X Y W` | Rollup under top |
| `rolldownd` | `X Y Z W -> Y Z X W` | Rolldown under top |
| `rotated` | `X Y Z W -> Z Y X W` | Rotate under top |

#### Time Operations
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `localtime` | `I -> T` | Convert time_t to local time struct |
| `gmtime` | `I -> T` | Convert time_t to UTC time struct |
| `mktime` | `T -> I` | Convert time struct to time_t |
| `strftime` | `T S1 -> S2` | Format time as string |

#### Formatting
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `format` | `N C I J -> S` | Format integer N with char C, width I, precision J |
| `formatf` | `F C I J -> S` | Format float F with char C, width I, precision J |

#### File I/O
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `fclose` | `S ->` | Close file stream |
| `feof` | `S -> S B` | Test end-of-file |
| `ferror` | `S -> S B` | Test file error |
| `fflush` | `S -> S` | Flush file stream |
| `fgetch` | `S -> S C` | Read character from file |
| `fgets` | `S -> S L` | Read line from file |
| `fopen` | `P M -> S` | Open file with path P and mode M |
| `fread` | `S I -> S L` | Read I bytes from file |
| `fwrite` | `S L -> S` | Write list L to file |
| `fremove` | `P -> B` | Remove file at path P |
| `frename` | `P1 P2 -> B` | Rename file from P1 to P2 |
| `fput` | `S X -> S` | Write X to file |
| `fputch` | `S C -> S` | Write character to file |
| `fputchars` | `S "abc.." -> S` | Write characters to file |
| `fputstring` | `S "abc.." -> S` | Write string to file |
| `fseek` | `S P W -> S` | Seek in file |
| `ftell` | `S -> S I` | Get file position |

#### Case/Switch
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `opcase` | `X [..[X Xs]..] -> [Xs]` | Case with quotation result |
| `case` | `X [..[X Y]..] -> Y i` | Case with immediate execution |

### Predicate (3)

| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `leaf` | `X -> B` | Test if X is a leaf (not aggregate) |
| `user` | `X -> B` | Test if X is user-defined |
| `file` | `F -> B` | Test if F is a file handle |

### Combinator (28)

#### Application Combinators
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `app1` | `X [P] -> R` | Apply P to X |
| `app11` | `X Y [P] -> R` | Apply P to X (Y unchanged) |
| `app12` | `X Y1 Y2 [P] -> R1 R2` | Apply P to X, two results |
| `app2` | `X1 X2 [P] -> R1 R2` | Apply P to X1 and X2 |
| `app3` | `X1 X2 X3 [P] -> R1 R2 R3` | Apply P to three values |
| `app4` | `X1 X2 X3 X4 [P] -> R1 R2 R3 R4` | Apply P to four values |

#### Arity Combinators
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `nullary` | `[P] -> R` | Execute P, push single result |
| `unary` | `X [P] -> R` | Execute P on X, push single result |
| `unary2` | `X1 X2 [P] -> R1 R2` | Execute P on X1 and X2 separately |
| `unary3` | `X1 X2 X3 [P] -> R1 R2 R3` | Execute P on three values |
| `unary4` | `X1 X2 X3 X4 [P] -> R1 R2 R3 R4` | Execute P on four values |
| `binary` | `X Y [P] -> R` | Execute P on X Y, push single result |
| `ternary` | `X Y Z [P] -> R` | Execute P on X Y Z, push single result |

#### Control Flow
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `construct` | `[P] [[P1] [P2] ..] -> R1 R2 ..` | Execute P, then each Pi |
| `cleave` | `X [P1] [P2] -> R1 R2` | Apply two quotations to X |

#### Type Conditionals
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `ifinteger` | `X [T] [E] -> ...` | If X is integer, execute T, else E |
| `ifchar` | `X [T] [E] -> ...` | If X is char, execute T, else E |
| `iflogical` | `X [T] [E] -> ...` | If X is boolean, execute T, else E |
| `ifset` | `X [T] [E] -> ...` | If X is set, execute T, else E |
| `ifstring` | `X [T] [E] -> ...` | If X is string, execute T, else E |
| `iflist` | `X [T] [E] -> ...` | If X is list, execute T, else E |
| `iffloat` | `X [T] [E] -> ...` | If X is float, execute T, else E |
| `iffile` | `X [T] [E] -> ...` | If X is file, execute T, else E |

#### Aggregate Combinators
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `some` | `A [B] -> X` | True if B holds for some element of A |
| `all` | `A [B] -> X` | True if B holds for all elements of A |

#### Tree Combinators
| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `treestep` | `T [P] -> ...` | Step through tree T with P |
| `treerec` | `T [O] [C] -> ...` | Tree recursion |
| `treegenrec` | `T [O1] [O2] [C] -> ...` | General tree recursion |

### Miscellaneous Commands (14)

| Primitive | Signature | Description |
|-----------|-----------|-------------|
| `help` | `->` | Display help |
| `helpdetail` | `[S1 S2 ..] ->` | Display detailed help for symbols |
| `manual` | `->` | Display full manual |
| `setautoput` | `I ->` | Set autoput flag |
| `setundeferror` | `I ->` | Set undeferror flag |
| `gc` | `->` | Force garbage collection |
| `system` | `"command" ->` | Execute shell command |
| `getenv` | `"variable" -> "value"` | Get environment variable |
| `argv` | `-> A` | Push command line arguments |
| `argc` | `-> I` | Push argument count |
| `get` | `-> F` | Read factor from input |
| `include` | `"filnam.ext" ->` | Include Joy source file |
| `abort` | `->` | Abort execution |
| `quit` | `->` | Quit interpreter |

---

## Priority

### High (commonly used)
- `some`, `all` - aggregate predicates
- `nullary`, `unary`, `binary`, `ternary` - arity combinators
- `cleave` - parallel application
- `leaf`, `file` - type predicates
- File I/O: `fopen`, `fclose`, `fread`, `fwrite`, `fgets`
- `system`, `getenv`, `argv`, `argc` - system interaction

### Medium
- Type conditionals (`ifinteger`, `ifchar`, etc.)
- Application combinators (`app1`, `app2`, etc.)
- Tree combinators
- Time operations (`localtime`, `gmtime`, `strftime`)

### Low (interpreter-specific)
- `help`, `helpdetail`, `manual`
- `conts`, `autoput`, `undeferror`, `echo`
- `gc`, `abort`, `quit`

---

## Test Status

**jp-nestrec.joy: PASSING** - All tests run successfully.

### Working Tests

| Test | Combinator | Status |
|------|------------|--------|
| r-fact | ifte | PASS |
| r-mcc91 | ifte | PASS |
| r-ack | cond | PASS |
| r-hamilhyp | ifte | PASS |
| x-fact | x | PASS |
| x-mcc91 | x | PASS |
| x-ack | x | PASS |
| y-ack | y | PASS |
| x-hamilhyp | x | PASS |
| l-mcc91 | linrec | PASS |
| l-ack | linrec | PASS |
| lr-hamilhyp | linrec | PASS |
| toggle | ifte | PASS |
| lr-grayseq | linrec | PASS |
| cnr-hamilhyp | condnestrec | PASS |
| cnr-ack | condnestrec | PASS |
| cnr-grayseq | condnestrec | PASS |
| cnr-hanoi | condnestrec | PASS |
| cnr-fact | condnestrec | PASS |
| cnr-mcc91 | condnestrec | PASS |
| cnr-even | condnestrec | PASS |
| cnr-abs | condnestrec | PASS |

### Test Commands

```bash
# Compile and run jp-nestrec.joy
uv run python -m pyjoy compile tests/examples/jp-nestrec.joy -o build -n jp-nestrec && ./build/jp-nestrec

# Run official Joy tests
uv run python -m pyjoy compile joy/test2/condlinrec.joy -o build -n test && ./build/test
```
