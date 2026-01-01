# Joy Manual

**Compiled at 16:57:51 on Mar 17 2003 (BDW)**
**Copyright 2001 by Manfred von Thun**

## Literal

### truth value type

```text
truth value type : -> B
```

The logical type, or the type of truth values.
It has just two literals: `true` and `false`.

### character type

```text
character type : -> C
```

The type of characters. Literals are written with a single quote.
Examples:  'A  '7  ';  and so on. Unix style escapes are allowed.

### integer type

```text
integer type : -> I
```

The type of negative, zero or positive integers.
Literals are written in decimal notation. Examples:  -123   0   42.

### set type

```text
set type : -> {...}
```

The type of sets of small non-negative integers.
The maximum is platform dependent, typically the range is 0..31.
Literals are written inside curly braces.
Examples:  {}  {0}  {1 3 5}  {19 18 17}.

### string type

```text
string type : -> "..."
```

The type of strings of characters. Literals are written inside double quotes.
Examples: ""  "A"  "hello world" "123".
Unix style escapes are accepted.

### list type

```text
list type : -> [...]
```

The type of lists of values of any type (including lists),
or the type of quoted programs which may contain operators or combinators.
Literals of this type are written inside square brackets.
Examples: `[]  [3 512 -7]  [john mary]  ['A 'C ['B]]  [dup *].`

### float type

```text
float type : -> F
```

The type of floating-point numbers.
Literals of this type are written with embedded decimal points (like 1.2)
and optional exponent specifiers (like 1.5E2)

### file type

```text
file type : -> FILE:
```

The type of references to open I/O streams,
typically but not necessarily files.
The only literals of this type are `stdin`, `stdout`, and `stderr`.

## Operand

### false

```text
false : -> false
```

Pushes the value `false`.

### true

```text
true : -> true
```

Pushes the value `true`.

### maxint

```text
maxint : -> maxint
```

Pushes largest integer (platform dependent). Typically it is 32 bits.

### setsize

```text
setsize : -> setsize
```

Pushes the maximum number of elements in a set (platform dependent).
Typically it is 32, and set members are in the range 0..31.

### stack

```text
stack : .. X Y Z -> .. X Y Z [Z Y X ..]
```

Pushes the stack as a list.

### conts

```text
conts : -> [[P] [Q] ..]
```

Pushes current continuations. Buggy, do not use.

### autoput

```text
autoput : -> I
```

Pushes current value of flag  for automatic output, I = 0..2.

### undeferror

```text
undeferror : -> I
```

Pushes current value of undefined-is-error flag.

### undefs

```text
undefs : ->
```

Push a list of all undefined symbols in the current symbol table.

### echo

```text
echo : -> I
```

Pushes value of echo flag, I = 0..3.

### clock

```text
clock : -> I
```

Pushes the integer value of current CPU usage in hundreds of a second.

### time

```text
time : -> I
```

Pushes the current time (in seconds since the Epoch).

### rand

```text
rand : -> I
```

I is a random integer.

### stdin

```text
stdin : -> S
```

Pushes the standard input stream.

### stdout

```text
stdout : -> S
```

Pushes the standard output stream.

### stderr

```text
stderr : -> S
```

Pushes the standard error stream.

## Operator

### id

```text
id : ->
```

Identity function, does nothing.
Any program of the form  P id Q  is equivalent to just  P Q.

### dup

```text
dup : X -> X X
```

Pushes an extra copy of X onto stack.

### swap

```text
swap : X Y -> Y X
```

Interchanges X and Y on top of the stack.

### rollup

```text
rollup : X Y Z -> Z X Y
```

Moves X and Y up, moves Z down

### rolldown

```text
rolldown : X Y Z -> Y Z X
```

Moves Y and Z down, moves X up

### rotate

```text
rotate : X Y Z -> Z Y X
```

Interchanges X and Z

### popd

```text
popd : Y Z -> Z
```

As if defined by:   popd  ==  [pop] dip

### dupd

```text
dupd : Y Z -> Y Y Z
```

As if defined by:   dupd  ==  [dup] dip

### swapd

```text
swapd : X Y Z -> Y X Z
```

As if defined by:   swapd  ==  [swap] dip

### rollupd

```text
rollupd : X Y Z W -> Z X Y W
```

As if defined by:   rollupd  ==  [rollup] dip

### rolldownd

```text
rolldownd : X Y Z W -> Y Z X W
```

As if defined by:   rolldownd  ==  [rolldown] dip

### rotated

```text
rotated : X Y Z W -> Z Y X W
```

As if defined by:   rotated  ==  [rotate] dip

### pop

```text
pop : X ->
```

Removes X from top of the stack.

### choice

```text
choice : B T F -> X
```

If B is `true`, then X = T else X = F.

### or

```text
or : X Y -> Z
```

Z is the union of sets X and Y, logical disjunction for truth values.

### xor

```text
xor : X Y -> Z
```

Z is the symmetric difference of sets X and Y,
logical exclusive disjunction for truth values.

### and

```text
and : X Y -> Z
```

Z is the intersection of sets X and Y, logical conjunction for truth values.

### not

```text
not : X -> Y
```

Y is the complement of set X, logical negation for truth values.

### +

```text
+ : M I -> N
```

Numeric N is the result of adding integer I to numeric M.
Also supports float.

### -

```text
- : M I -> N
```

Numeric N is the result of subtracting integer I from numeric M.
Also supports float.

### *

```text
* : I J -> K
```

Integer K is the product of integers I and J.  Also supports float.

### /

```text
/ : I J -> K
```

Integer K is the (rounded) ratio of integers I and J.  Also supports float.

### rem

```text
rem : I J -> K
```

Integer K is the remainder of dividing I by J.  Also supports float.

### div

```text
div : I J -> K L
```

Integers K and L are the quotient and remainder of dividing I by J.

### sign

```text
sign : N1 -> N2
```

Integer N2 is the sign (-1 or 0 or +1) of integer N1,
or float N2 is the sign (-1.0 or 0.0 or 1.0) of float N1.

### neg

```text
neg : I -> J
```

Integer J is the negative of integer I.  Also supports float.

### ord

```text
ord : C -> I
```

Integer I is the Ascii value of character C (or logical or integer).

### chr

```text
chr : I -> C
```

C is the character whose Ascii value is integer I (or logical or character).

### abs

```text
abs : N1 -> N2
```

Integer N2 is the absolute value (0,1,2..) of integer N1,
or float N2 is the absolute value (0.0 ..) of float N1

### acos

```text
acos : F -> G
```

G is the arc cosine of F.

### asin

```text
asin : F -> G
```

G is the arc sine of F.

### atan

```text
atan : F -> G
```

G is the arc tangent of F.

### atan2

```text
atan2 : F G -> H
```

H is the arc tangent of F / G.

### ceil

```text
ceil : F -> G
```

G is the float ceiling of F.

### cos

```text
cos : F -> G
```

G is the cosine of F.

### cosh

```text
cosh : F -> G
```

G is the hyperbolic cosine of F.

### exp

```text
exp : F -> G
```

G is e (2.718281828...) raised to the Fth power.

### floor

```text
floor : F -> G
```

G is the floor of F.

### frexp

```text
frexp : F -> G I
```

G is the mantissa and I is the exponent of F.
Unless F = 0, 0.5 <= abs(G) < 1.0.

### ldexp

```text
ldexp : F I -> G
```

G is F times 2 to the Ith power.

### log

```text
log : F -> G
```

G is the natural logarithm of F.

### log10

```text
log10 : F -> G
```

G is the common logarithm of F.

### modf

```text
modf : F -> G H
```

G is the fractional part and H is the integer part
(but expressed as a float) of F.

### pow

```text
pow : F G -> H
```

H is F raised to the Gth power.

### sin

```text
sin : F -> G
```

G is the sine of F.

### sinh

```text
sinh : F -> G
```

G is the hyperbolic sine of F.

### sqrt

```text
sqrt : F -> G
```

G is the square root of F.

### tan

```text
tan : F -> G
```

G is the tangent of F.

### tanh

```text
tanh : F -> G
```

G is the hyperbolic tangent of F.

### trunc

```text
trunc : F -> I
```

I is an integer equal to the float F truncated toward zero.

### localtime

```text
localtime : I -> T
```

Converts a time I into a list T representing local time:

`[year month day hour minute second isdst yearday weekday].`

Month is 1 = January ... 12 = December;
isdst is a Boolean flagging daylight savings/summer time;
weekday is 0 = Monday ... 7 = Sunday.

### gmtime

```text
gmtime : I -> T
```

Converts a time I into a list T representing universal time:

`[year month day hour minute second isdst yearday weekday].`

Month is 1 = January ... 12 = December;
isdst is `false`; weekday is 0 = Monday ... 7 = Sunday.

### mktime

```text
mktime : T -> I
```

Converts a list T representing local time into a time I.
T is in the format generated by localtime.

### strftime

```text
strftime : T S1 -> S2
```

Formats a list T in the format of localtime or gmtime
using string S1 and pushes the result S2.

### strtol

```text
strtol : S I -> J
```

String S is converted to the integer J using base I.
If I = 0, assumes base 10,
but leading "0" means base 8 and leading "0x" means base 16.

### strtod

```text
strtod : S -> R
```

String S is converted to the float R.

### format

```text
format : N C I J -> S
```

S is the formatted version of N in mode C
('d or 'i = decimal, 'o = octal, 'x or
'X = hex with lower or upper case letters)
with maximum width I and minimum width J.

### formatf

```text
formatf : F C I J -> S
```

S is the formatted version of F in mode C
('e or 'E = exponential, 'f = fractional,
'g or G = general with lower or upper case letters)
with maximum width I and precision J.

### srand

```text
srand : I ->
```

Sets the random integer seed to integer I.

### pred

```text
pred : M -> N
```

Numeric N is the predecessor of numeric M.

### succ

```text
succ : M -> N
```

Numeric N is the successor of numeric M.

### max

```text
max : N1 N2 -> N
```

N is the maximum of numeric values N1 and N2.  Also supports float.

### min

```text
min : N1 N2 -> N
```

N is the minimum of numeric values N1 and N2.  Also supports float.

### fclose

```text
fclose : S ->
```

Stream S is closed and removed from the stack.

### feof

```text
feof : S -> S B
```

B is the end-of-file status of stream S.

### ferror

```text
ferror : S -> S B
```

B is the error status of stream S.

### fflush

```text
fflush : S -> S
```

Flush stream S, forcing all buffered output to be written.

### fgetch

```text
fgetch : S -> S C
```

C is the next available character from stream S.

### fgets

```text
fgets : S -> S L
```

L is the next available line (as a string) from stream S.

### fopen

```text
fopen : P M -> S
```

The file system object with pathname P is opened with mode M (r, w, a, etc.)
and stream object S is pushed; if the open fails, file:NULL is pushed.

### fread

```text
fread : S I -> S L
```

I bytes are read from the current position of stream S
and returned as a list of I integers.

### fwrite

```text
fwrite : S L -> S
```

A list of integers are written as bytes to the current position of stream S.

### fremove

```text
fremove : P -> B
```

The file system object with pathname P is removed from the file system.
is a boolean indicating success or failure.

### frename

```text
frename : P1 P2 -> B
```

The file system object with pathname P1 is renamed to P2.
B is a boolean indicating success or failure.

### fput

```text
fput : S X -> S
```

Writes X to stream S, pops X off stack.

### fputch

```text
fputch : S C -> S
```

The character C is written to the current position of stream S.

### fputchars

```text
fputchars : S "abc.." -> S
```

The string abc.. (no quotes) is written to the current position of stream S.

### fputstring

```text
fputstring : S "abc.." -> S
```

== fputchars, as a temporary alternative.

### fseek

```text
fseek : S P W -> S
```

Stream S is repositioned to position P relative to whence-point W,
where W = 0, 1, 2 for beginning, current position, end respectively.

### ftell

```text
ftell : S -> S I
```

I is the current position of stream S.

### unstack

```text
unstack : [X Y ..] -> ..Y X
```

The list [X Y ..] becomes the new stack.

### cons

```text
cons : X A -> B
```

Aggregate B is A with a new member X (first member for sequences).

### swons

```text
swons : A X -> B
```

Aggregate B is A with a new member X (first member for sequences).

### first

```text
first : A -> F
```

F is the first member of the non-empty aggregate A.

### rest

```text
rest : A -> R
```

R is the non-empty aggregate A with its first member removed.

### compare

```text
compare : A B -> I
```

I (=-1,0,+1) is the comparison of aggregates A and B.
The values correspond to the predicates <=, =, >=.

### at

```text
at : A I -> X
```

X (= A[I]) is the member of A at position I.

### of

```text
of : I A -> X
```

X (= A[I]) is the I-th member of aggregate A.

### size

```text
size : A -> I
```

Integer I is the number of elements of aggregate A.

### opcase

```text
opcase : X [..[X Xs]..] -> [Xs]
```

Indexing on type of X, returns the list [Xs].

### case

```text
case : X [..[X Y]..] -> Y i
```

Indexing on the value of X, execute the matching Y.

### uncons

```text
uncons : A -> F R
```

F and R are the first and the rest of non-empty aggregate A.

### unswons

```text
unswons : A -> R F
```

R and F are the rest and the first of non-empty aggregate A.

### drop

```text
drop : A N -> B
```

Aggregate B is the result of deleting the first N elements of A.

### take

```text
take : A N -> B
```

Aggregate B is the result of retaining just the first N elements of A.

### concat

```text
concat : S T -> U
```

Sequence U is the concatenation of sequences S and T.

### enconcat

```text
enconcat : X S T -> U
```

Sequence U is the concatenation of sequences S and T
with X inserted between S and T (== swapd cons concat)

### name

```text
name : sym -> "sym"
```

For operators and combinators, the string "sym" is the name of item sym,
for literals sym the result string is its type.

### intern

```text
intern : "sym" -> sym
```

Pushes the item whose name is "sym".

### body

```text
body : U -> [P]
```

Quotation [P] is the body of user-defined symbol U.

## Predicate

### null

```text
null : X -> B
```

Tests for empty aggregate X or zero numeric.

### small

```text
small : X -> B
```

Tests whether aggregate X has 0 or 1 members, or numeric 0 or 1.

### >=

```text
>= : X Y -> B
```

Either both X and Y are numeric or both are strings or symbols.
Tests whether X greater than or equal to Y.  Also supports float.

### >

```text
> : X Y -> B
```

Either both X and Y are numeric or both are strings or symbols.
Tests whether X greater than Y.  Also supports float.

### <=

```text
<= : X Y -> B
```

Either both X and Y are numeric or both are strings or symbols.
Tests whether X less than or equal to Y.  Also supports float.

### <

```text
< : X Y -> B
```

Either both X and Y are numeric or both are strings or symbols.
Tests whether X less than Y.  Also supports float.
!=      :  X Y  ->  B
Either both X and Y are numeric or both are strings or symbols.
Tests whether X not equal to Y.  Also supports float.

### =

```text
= : X Y -> B
```

Either both X and Y are numeric or both are strings or symbols.
Tests whether X equal to Y.  Also supports float.

### equal

```text
equal : T U -> B
```

(Recursively) tests whether trees T and U are identical.

### has

```text
has : A X -> B
```

Tests whether aggregate A has X as a member.

### in

```text
in : X A -> B
```

Tests whether X is a member of aggregate A.

### integer

```text
integer : X -> B
```

Tests whether X is an integer.

### char

```text
char : X -> B
```

Tests whether X is a character.

### logical

```text
logical : X -> B
```

Tests whether X is a logical.

### set

```text
set : X -> B
```

Tests whether X is a set.

### string

```text
string : X -> B
```

Tests whether X is a string.

### list

```text
list : X -> B
```

Tests whether X is a list.

### leaf

```text
leaf : X -> B
```

Tests whether X is not a list.

### user

```text
user : X -> B
```

Tests whether X is a user-defined symbol.

### float

```text
float : R -> B
```

Tests whether R is a float.

### file

```text
file : F -> B
```

Tests whether F is a file.

## Combinator

### i

```text
i : [P] -> ...
```

Executes P. So, [P] i  ==  P.

### x

```text
x : [P]i -> ...
```

Executes P without popping [P]. So, [P] x  ==  [P] P.

### dip

```text
dip : X [P] -> ... X
```

Saves X, executes P, pushes X back.

### app1

```text
app1 : X [P] -> R
```

Executes P, pushes result R on stack without X.

### app11

```text
app11 : X Y [P] -> R
```

Executes P, pushes result R on stack.

### app12

```text
app12 : X Y1 Y2 [P] -> R1 R2
```

Executes P twice, with Y1 and Y2, returns R1 and R2.

### construct

```text
construct : [P] [[P1] [P2] ..] -> R1 R2 ..
```

Saves state of stack and then executes [P].
Then executes each [Pi] to give Ri pushed onto saved stack.

### nullary

```text
nullary : [P] -> R
```

Executes P, which leaves R on top of the stack.
No matter how many parameters this consumes, none are removed from the stack.

### unary

```text
unary : X [P] -> R
```

Executes P, which leaves R on top of the stack.
No matter how many parameters this consumes,
exactly one is removed from the stack.

### unary2

```text
unary2 : X1 X2 [P] -> R1 R2
```

Executes P twice, with X1 and X2 on top of the stack.
Returns the two values R1 and R2.

### unary3

```text
unary3 : X1 X2 X3 [P] -> R1 R2 R3
```

Executes P three times, with Xi, returns Ri (i = 1..3).

### unary4

```text
unary4 : X1 X2 X3 X4 [P] -> R1 R2 R3 R4
```

Executes P four times, with Xi, returns Ri (i = 1..4).

### app2

```text
app2 : X1 X2 [P] -> R1 R2
```

Obsolescent.  == unary2

### app3

```text
app3 : X1 X2 X3 [P] -> R1 R2 R3
```

Obsolescent.  == unary3

### app4

```text
app4 : X1 X2 X3 X4 [P] -> R1 R2 R3 R4
```

Obsolescent.  == unary4

### binary

```text
binary : X Y [P] -> R
```

Executes P, which leaves R on top of the stack.
No matter how many parameters this consumes,
exactly two are removed from the stack.

### ternary

```text
ternary : X Y Z [P] -> R
```

Executes P, which leaves R on top of the stack.
No matter how many parameters this consumes,
exactly three are removed from the stack.

### cleave

```text
cleave : X [P1] [P2] -> R1 R2
```

Executes P1 and P2, each with X on top, producing two results.

### branch

```text
branch : B [T] [F] -> ...
```

If B is `true`, then executes T else executes F.

### ifte

```text
ifte : [B] [T] [F] -> ...
```

Executes B. If that yields `true`, then executes T else executes F.

### ifinteger

```text
ifinteger : X [T] [E] -> ...
```

If X is an integer, executes T else executes E.

### ifchar

```text
ifchar : X [T] [E] -> ...
```

If X is a character, executes T else executes E.

### iflogical

```text
iflogical : X [T] [E] -> ...
```

If X is a logical or truth value, executes T else executes E.

### ifset

```text
ifset : X [T] [E] -> ...
```

If X is a set, executes T else executes E.

### ifstring

```text
ifstring : X [T] [E] -> ...
```

If X is a string, executes T else executes E.

### iflist

```text
iflist : X [T] [E] -> ...
```

If X is a list, executes T else executes E.

### iffloat

```text
iffloat : X [T] [E] -> ...
```

If X is a float, executes T else executes E.

### iffile

```text
iffile : X [T] [E] -> ...
```

If X is a file, executes T else executes E.

### cond

```text
cond : [..[[Bi] Ti]..[D]] -> ...
```

Tries each Bi. If that yields `true`, then executes Ti and exits.
If no Bi yields `true`, executes default D.

### while

```text
while : [B] [D] -> ...
```

While executing B yields `true` executes D.

### linrec

```text
linrec : [P] [T] [R1] [R2] -> ...
```

Executes P. If that yields `true`, executes T.
Else executes R1, recurses, executes R2.

### tailrec

```text
tailrec : [P] [T] [R1] -> ...
```

Executes P. If that yields `true`, executes T.
Else executes R1, recurses.

### binrec

```text
binrec : [B] [T] [R1] [R2] -> ...
```

Executes P. If that yields `true`, executes T.
Else uses R1 to produce two intermediates, recurses on both,
then executes R2 to combines their results.

### genrec

```text
genrec : [B] [T] [R1] [R2] -> ...
```

Executes B, if that yields `true` executes T.
Else executes R1 and then `[[B] [T] [R1] [R2] genrec]` R2.

### condlinrec

```text
condlinrec : [ [C1] [C2] .. [D] ] -> ...
```

Each `[Ci]` is of the forms `[[B] [T]]` or `[[B] [R1] [R2]]`.
Tries each B. If that yields `true` and there is just a [T], executes T and exit.
If there are `[R1]` and `[R2]`, executes R1, recurses, executes R2.
Subsequent case are ignored. If no B yields `true`, then [D] is used.
It is then of the forms `[[T]]` or `[[R1] [R2]]`. For the former, executes T.
For the latter executes R1, recurses, executes R2.

### step

```text
step : A [P] -> ...
```

Sequentially putting members of aggregate A onto stack,
executes P for each member of A.

### fold

```text
fold : A V0 [P] -> V
```

Starting with value V0, sequentially pushes members of aggregate A
and combines with binary operator P to produce value V.

### map

```text
map : A [P] -> B
```

Executes P on each member of aggregate A,
collects results in sametype aggregate B.

### times

```text
times : N [P] -> ...
```

N times executes P.

### infra

```text
infra : L1 [P] -> L2
```

Using list L1 as stack, executes P and returns a new list L2.
The first element of L1 is used as the top of stack,
and after execution of P the top of stack becomes the first element of L2.

### primrec

```text
primrec : X [I] [C] -> R
```

Executes I to obtain an initial value R0.
For integer X uses increasing positive integers to X, combines by C for new R.
For aggregate X uses successive members and combines by C for new R.

### filter

```text
filter : A [B] -> A1
```

Uses test B to filter aggregate A producing sametype aggregate A1.

### split

```text
split : A [B] -> A1 A2
```

Uses test B to split aggregate A into sametype aggregates A1 and A2 .

### some

```text
some : A [B] -> X
```

Applies test B to members of aggregate A, X = `true` if some pass.

### all

```text
all : A [B] -> X
```

Applies test B to members of aggregate A, X = `true` if all pass.

### treestep

```text
treestep : T [P] -> ...
```

Recursively traverses leaves of tree T, executes P for each leaf.

### treerec

```text
treerec : T [O] [C] -> ...
```

T is a tree. If T is a leaf, executes O. Else executes `[[O] [C] treerec] C.`

### treegenrec

```text
treegenrec : T [O1] [O2] [C] -> ...
```

T is a tree. If T is a leaf, executes O1.
Else executes O2 and then `[[O1] [O2] [C] treegenrec] C.`

## Miscellaneous Commands

### help

```text
help : ->
```

Lists all defined symbols, including those from library files.
Then lists all primitives of raw Joy

(There is a variant: "`_help`" which lists hidden symbols).

`helpdetail      :  [ S1  S2  .. ]`

Gives brief help on each symbol S in the list.

### manual

```text
manual : ->
```

Writes this manual of all Joy primitives to output file.

### setautoput

```text
setautoput : I ->
```

Sets value of flag for automatic put to I (if I = 0, none;
if I = 1, put; if I = 2, stack.

### setundeferror

```text
setundeferror : I ->
```

Sets flag that controls behavior of undefined functions
(0 = no error, 1 = error).

### setecho

```text
setecho : I ->
```

Sets value of echo flag for listing.
I = 0: no echo, 1: echo, 2: with tab, 3: and linenumber.

### gc

```text
gc : ->
```

Initiates garbage collection.

### system

```text
system : "command" ->
```

Escapes to shell, executes string "command".
The string may cause execution of another program.
When that has finished, the process returns to Joy.

### getenv

```text
getenv : "variable" -> "value"
```

Retrieves the value of the environment variable "variable".

### argv

```text
argv : -> A
```

Creates an aggregate A containing the interpreter's command line arguments.

### argc

```text
argc : -> I
```

Pushes the number of command line arguments. This is quivalent to 'argv size'.

### get

```text
get : -> F
```

Reads a factor from input and pushes it onto stack.

### put

```text
put : X ->
```

Writes X to output, pops X off stack.

### putch

```text
putch : N ->
```

N : numeric, writes character whose ASCII is N.

### putchars

```text
putchars : "abc.." ->
```

Writes  abc.. (without quotes)

### include

```text
include : "filnam.ext" ->
```

Transfers input to file whose name is "filnam.ext".
On end-of-file returns to previous input file.

### abort

```text
abort : ->
```

Aborts execution of current Joy program, returns to Joy main cycle.

### quit

```text
quit : ->
```

Exit from Joy.
