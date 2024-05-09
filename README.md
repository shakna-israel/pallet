# pallet

A stack-oriented programming interpreter.

---

* [Hello World](#hello-world)

* [Introduction](#introduction)

* [Variables](#variables)


---

## Hello World

The famous 'Hello, World!' program is a simple program that can output a message to the screen.

In *pallet*, it is as simple as you might expect:

	print! 'Hello, World!'

To break it down further, you push a string with your message to the stack, push the print symbol to the stack, and then call it from the environment:

	'Hello, World!'

	print

	call!

In *pallet*, each line of a program is parsed from right-to-left, rather than the other way around. This is mostly because it's a stack-oriented language, but we still want it easily readable.

To give another example:

	add! 1 3

This little program runs in this order:

	3

	1

	add

	call!

Every item that isn't a call is pushed to the top of a list that we refer to as the `stack`. This list is then passed to the executing call to decide what, if anything, to do with it.

---

## Introduction

*pallet* is a highly flexible stack-oriented programming language.

	print! "Hello, World!"

The language is intended to be easily readable, easy for beginner programmers to learn, whilst simultaneously possessing fantastic metaprogramming abilities.

Metaprogramming is something that tends to be reserved for either highly complicated languages, or for extremely complex interfaces. Yet, it is something a programmer may still find themself reaching for the moment they go off the beaten track.

Creating something new shouldn't require strict discipline. It's an artform. Creativity should be allowed to flow freely.

	if! (equal? a b) {

		print! "True!"

	} else {

		print! "False!"

	}

This little bit of code should feel mostly familiar. It feels a lot like many programming languages out there. However, the exact construction of this statement is actually wildly different.

First, `if` is actually an ordinary function call. It is not a keyword or an inbuilt language construct. Which means it can be safely removed, if you feel the need. Or replaced, etc.

Secondly, the bracketed sections are a type of list called a `block` by *pallet*. They're not statements. They're an ordinary list, which could be replaced by a variable reference - allowing you to manipulate the sections as you need.

Thirdly, `else` is a `symbol` type. It is not a keyword. The `if` function checks the stack for it, which means you can conditionally generate an `else` if you want one.

In short, everything you see above can be generated at runtime. Everything can be manipulated.

	= cond (equal? a b)

	(print! "True!"); = truthy

	= falsey (print! 'False!')

	= maybe `'else'

	= func if

	! $func $cond $truthy $maybe $falsey

This little bit of code is exactly identical to the one from before. The only difference is, we're storing and calling our variables.

---

## Variables

Strictly speaking, variables don't exactly exist in *pallet*.

Rather, when you use the `assign` function from the Standard Library, it generates a function that copies a value onto the `stack` when called.

The `get` call simply runs that function, and if nothing was output, puts a `null` onto the stack instead.

Thus, these two lines are very similar:

	$a

	a!

There are two ways to do an assignment. Both call the `assign` function from the Standard Library, if it is available. (You can of course override the symbol in your environment.)

	= VariableName VariableValue

	assign! VariableName VariableValue

The environment is scoped, with shadowing rather than overwriting. The `begin` function from the Standard Library appends a new environment table, and `end` removes it.

	= a 'Outer'

	begin!

		= a 'Inner'

		print! $a

	end!

	print! $a

Of course, if the variable is in the same environment as the new assignment, it is overwritten.

	= a 'Original'

	= a 'Overwritten'

	print! $a

---

(c) James Milne


