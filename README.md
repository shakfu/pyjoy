# pyjoy

Towards a python implementation of Manfred von Thun's Joy Language.

The primary aim of this project is to accurately implement the Joy language (see `joy/`) in python3  (see `docs/pyjoy.md`). The priority is to have an accurate implementation which can run joy programs without issue. A secondary aim is to have the python implementation generate c code which could then be compiled into machine code. This is consistent with the late Manfred von Thun's wish:

> Several other people have published other more or less complete Joy
> interpreters, written in ML and in Scheme, in the "concatenative" mailing group.
> At this point in time I have no plans to write a full compiler.  A first
> version of such a compiler would presumably use C as an intermediate language
> and leave the generation of machine code to the C compiler.  I would very much
> welcome if somebody were to take up the task." [A Conversation with Manfred von Thun](https://www.nsl.com/papers/interview.htm)

There's also a sister [pyjoy2](https://github.com/shakfu/pyjoy2) project that has a different aim of Pythonically re-imagining the Joy language, and where accuracy of the implementation is not a primary goal.

