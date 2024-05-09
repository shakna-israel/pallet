import copy

def check_token(item):
	if item[0] == "call!":
		yield ("call", "call", *item)
	elif len(item[0]) > 1 and item[0].startswith("$"):
		yield ("get", "get", *item)
		t = [*item]
		t[0] = item[0][1:]
		for row in check_token(tuple(t)):
			yield row
	elif len(item[0]) > 1 and item[0].startswith("`"):
		yield ("call", "call", *item)
		yield ("symbol", "tosymbol", *item)
		t = [*item]
		t[0] = item[0][1:]
		for row in check_token(tuple(t)):
			yield row
	elif len(item[0]) > 1 and item[0].endswith("!"):
		yield ("call", "call", *item)
		t = [*item]
		t[0] = item[0][:-1]
		for row in check_token(tuple(t)):
			yield row
	elif len(item[0]) > 1 and item[0].endswith("?"):
		yield ("call", "call", *item)
		yield ("symbol", "toboolean", *item)
		yield ("get", "get", *item)
		t = [*item]
		t[0] = item[0][:-1]
		for row in check_token(tuple(t)):
			yield row
	elif item[0] == '+':
		yield ("call", "call", *item)
		yield ("symbol", "add", *item)
	elif item[0] == '-':
		yield ("call", "call", *item)
		yield ("symbol", "minus", *item)
	elif item[0] == '*':
		yield ("call", "call", *item)
		yield ("symbol", "multiply", *item)
	elif item[0] == '/':
		yield ("call", "call", *item)
		yield ("symbol", "divide", *item)
	elif item[0] == '=':
		yield ("call", "call", *item)
		yield ("symbol", "assign", *item)
	elif item[0] == '==':
		yield ("call", "call", *item)
		yield ("symbol", "equal", *item)
	elif item[0] == '!=':
		yield ("call", "call", *item)
		yield ("symbol", "equal", *item)
		yield ("call", "call", *item)
		yield ("symbol", "not", *item)
	elif len(item[0]) > 1 and ((item[0].startswith('"') and item[0].endswith('"')) or (item[0].startswith("'") and item[0].endswith("'"))):
		yield ("string", item[0][1:-1], *item)
	elif item[0] == '!':
		yield ("call", "call", *item)
	elif item[0] == '?':
		yield ("call", "call", *item)
		yield ("symbol", "toboolean", *item)
		yield ("get", "get", *item)
	elif item[0] == '$' or item[0] == 'get':
		yield ("get", "get", *item)
	elif item[0] == '`':
		yield ("call", "call", *item)
		yield ("symbol", "tosymbol", *item)
	elif item[0].isdigit():
		yield ("integer", int(item[0]), *item)
	elif item[0].count(".") == 1 and item[0].replace(".", "").isdigit():
		yield ("float", float(item[0]), *item)
	elif item[0] == 'true' or item[0] == 'false':
		yield ("boolean", item[0] == "true", *item)
	elif item[0] == 'null':
		yield ("null", None, *item)
	elif len(item[0]) > 1 and (
		(item[0].startswith("(") and item[0].endswith(")")) or
		(item[0].startswith("{") and item[0].endswith("}")) or
		(item[0].startswith("[") and item[0].endswith("]"))):

		yield ("block", list(parse(item[0][1:-1], line=item[1], char=item[2])), *item)
	
	else:
		yield ("symbol", item[0], *item)

def check_statement(statement):
	r = []

	for item in statement:
		for row in check_token(item):
			r.append(row)

	return reversed(r)

def parse(source, line=1, char=0):
	statement = []
	token = []
	debug = {}

	in_string = False
	in_expression = 0
	expression_type = False
	in_comment = False

	for c in source:
		if c == '\n':
			line += 1
			char = 0
		else:
			char += 1

		try:
			debug['line']
		except KeyError:
			debug['line'] = line
			debug['char'] = char

		if in_comment:
			# We append and then drop comments, to allow for escaping inside them.
			if token[-1:] and token[-1] == '\\':
				token[-1] = c
				token.append('')
			elif c == in_comment:
				token = []
				debug = {}
				in_comment = False
			else:
				token.append(c)
		elif in_string:
			if token[-1:] and token[-1] == '\\':
				if c == 'n':
					token[-1] = '\n'
					token.append('')
				else:
					token[-1] = c
					token.append('')
			elif c == in_string:
				token.append(c)

				if in_expression < 1:
					statement.append((''.join(token), debug['line'], debug['char'], line, char))
					debug = {}
					token = []
				in_string = False
			else:
				token.append(c)
		elif in_expression > 0:
			if c == expression_type:
				token.append(c)
				in_expression += 1
			elif (expression_type == '(' and c == ')') or (expression_type == '{' and c == "}") or (expression_type == "[" and c == "]"):
				token.append(c)
				in_expression -= 1
			elif c in ["'", '"']:
				token.append(c)
				in_string = c
			else:
				token.append(c)

			if in_expression < 1:
				expression_type = False

		elif c in [' ', '\t', ',', '|']:
			if token:
				statement.append((''.join(token), debug['line'], debug['char'], line, char))
				debug = {}
				token = []
		elif c in [';', '\n']:
			if token:
				statement.append((''.join(token), debug['line'], debug['char'], line, char))
				debug = {}
				token = []
			if statement:
				for t in check_statement(statement):
					yield t
			statement = []
		elif c in ['"', "'"]:
			if token:
				statement.append((''.join(token), debug['line'], debug['char'], line, char))
				debug = {}
				token = []
			token.append(c)
			in_string = c
		elif c in ["(", "[", "{"]:
			if token:
				statement.append((''.join(token), debug['line'], debug['char'], line, char))
				debug = {}
				token = []
			token.append(c)
			in_expression += 1
			expression_type = c
		elif c in ['#', '~']:
			if token:
				statement.append((''.join(token), debug['line'], debug['char'], line, char))
			token = [c]
			debug = {}
			in_comment = c
		else:
			token.append(c)

	if token:
		statement.append((''.join(token), debug['line'], debug['char'], line, char))
	if statement:
		for t in check_statement(statement):
			yield t

# TODO: replace stack.pop with an null generating thing. (In case of empty stack.)

def load(filename):
	with open(filename) as openFile:
		datum = openFile.read()
		yield ["source", list(parse(datum)), filename, 1, 0, datum.count("\n") + 1, 0]

def loads(query):
	yield ['source', list(parse(query)), "string", 1, 0, query.count("\n") + 1, 0]

def call(item, tree, env, stack):
	try:
		caller = stack.pop()
	except IndexError:
		# TODO: Error, bad call.
		print("BAD CALL, empty stack", item)
		return tree, env, stack

	if caller[0] == 'error':
		# TODO: Error raise somehow.
		print("ERROR", caller)
		return tree, env, stack
	elif caller[0] == 'block':
		# Evaluate it:
		env.append({})
		if not evaluate(caller[1], env):
			print("BLOCK CALL ERROR", caller)
			return tree, env, stack
		env.pop()
	elif caller[0] == 'symbol':
		# Look up and call it:
		value = None
		for environ in reversed(env):
			try:
				value = environ[caller[1]]
				break
			except KeyError:
				pass

		if value == None:
			# TODO: Error
			print("BAD CALL", caller)
			return tree, env, stack
		else:
			if callable(value):
				tree, env, stack = value(item, tree, env, stack)
				return tree, env, stack
			else:
				stack.append(value)
				return tree, env, stack

	elif caller[0] == 'source':
		env.append({})
		if evaluate(caller[1], env, stack):
			env.pop()
			return tree, env, stack
		else:
			# TODO: Error
			print("BAD CALL", caller)
			return tree, env, stack
	else:
		# TODO: Error.
		print("BAD CALL", caller)
		return tree, env, stack

	return tree, env, stack

def get(item, tree, env, stack):
	try:
		caller = stack.pop()
	except IndexError:
		# TODO: Error, bad call.
		print("BAD GET, empty stack", item)
		return tree, env, stack

	if caller[0] == 'block':
		# Evaluate it:
		env.append({})
		if not evaluate(caller[1], env):
			print("BLOCK CALL ERROR", caller)
			return tree, env, stack
		env.pop()
	elif caller[0] == 'symbol':
		# Look up and call it:
		value = None
		for environ in reversed(env):
			try:
				value = environ[caller[1]]
				break
			except KeyError:
				pass

		if value == None:
			r = list(item)
			r[0] = "null"
			r[1] = None
			stack.append(r)
			return tree, env, stack
		else:
			if callable(value):
				tree, env, stack = value(item, tree, env, stack)
				return tree, env, stack
			else:
				stack.append(value)
				return tree, env, stack

	elif caller[0] == 'source':
		env.append({})
		if evaluate(caller[1], env, stack):
			env.pop()
			return tree, env, stack
		else:
			# TODO: Error
			print("BAD GET", caller)
			return tree, env, stack
	else:
		# TODO: Error.
		print("BAD GET", caller)
		return tree, env, stack

	return tree, env, stack

def std_version(item, tree, env, stack):
	r = list(item)
	r[0] = "string"
	r[1] = "PREALPHA"
	stack.append(r)
	return tree, env, stack

def std_add(item, tree, env, stack):
	a = stack.pop()
	b = stack.pop()

	r = list(item)
	r[0] = a[0]
	r[1] = a[1] + b[1]

	stack.append(tuple(r))

	return tree, env, stack

def std_print(item, tree, env, stack):
	v = stack.pop()

	print_value = ""
	if v[0] == 'null':
		print_value = "null"
	elif v[0] == 'boolean':
		if v[1]:
			print_value = "true"
		else:
			print_value = "false"
	elif v[0] == 'symbol':
		print_value = "`" + v[1]
	else:
		print_value = v[1]

	# TODO: Blocks and other types...

	print(print_value)

	return tree, env, stack

def std_type(item, tree, env, stack):
	a = stack.pop()

	r = list(item)
	r[0] = 'string'
	r[1] = a[0]

	stack.append(tuple(r))

	return tree, env, stack

def std_assign(item, tree, env, stack):
	name = stack.pop()
	value = stack.pop()

	env[-1][name[1]] = value

	return tree, env, stack

def std_begin(item, tree, env, stack):
	env.append({})

	return tree, env, stack

def std_end(item, tree, env, stack):
	env.pop()

	return tree, env, stack

def std_drop(item, tree, env, stack):
	# Clear the stack
	return tree, env, []

def std_doc(item, tree, env, stack):
	o = stack.pop()
	doc = stack.pop()

	# TODO: Install string of help

	return tree, env, stack

def std_help(item, tree, env, stack):
	o = stack.pop()

	# TODO: Get string of help

	return tree, env, stack

def std_toboolean(item, tree, env, stack):
	o = stack.pop()

	# TODO: Push bool

	return tree, env, stack

def std_tosymbol(item, tree, env, stack):
	o = list(stack.pop())
	o[0] = 'symbol'
	o[1] = str(o[1])
	stack.append(tuple(o))

	return tree, env, stack

def std_raise(item, tree, env, stack):
	o = stack.pop()

	r = list(item)
	r[0] = 'error'
	r[1] = o[1]
	stack.append(tuple(r))

	return tree, env, stack

def std_load(item, tree, env, stack):
	filename = stack.pop()
	data = list(load(filename[1]))
	stack.append(data[0])

	return tree, env, stack

def std_import(item, tree, env, stack):
	filename = stack.pop()

	# TODO: Search for filename...

	data = list(load(filename[1]))

	renv = copy.deepcopy(env)

	for environ in renv:
		try:
			rep = list(environ['#MAIN#'])
			rep[2] = False
			environ['#MAIN#'] = tuple(rep)
		except KeyError:
			pass

	rstack = []
	if not evaluate(data, renv, stack):
		# TODO: Raise an error
		print("IMPORT ERROR", renv, rstack)

	env.append({})

	display_name = filename[1].split(".", 1)[0]

	for environ in renv[1:]:
		for k, v in environ.items():
			if k.startswith("EXPORT:"):
				new_k = "{}.{}".format(display_name, k[7:])
				env[-1][new_k] = v

	return tree, env, stack

def std_export(item, tree, env, stack):
	symbol_name = stack.pop()
	value = stack.pop()

	symbol_name = "EXPORT:" + symbol_name[1]

	env[-1][symbol_name] = value

	return tree, env, stack

def std_equal(item, tree, env, stack):
	a = stack.pop()
	b = stack.pop()

	r = list(item)
	r[0] = 'boolean'

	if a[0] == b[0] and a[1] == b[1]:
		r[1] = True
		stack.append(r)
	else:
		r[1] = False
		stack.append(r)

	return tree, env, stack

def std_block(item, tree, env, stack):
	# Push an empty block for manipulating...

	block = list(item)
	block[0] = 'block'
	block[1] = []
	stack.append(tuple(block))

	return tree, env, stack

def std_boolean(item, tree, env, stack):
	o = list(item)
	o[0] = 'boolean'
	o[1] = True
	stack.append(tuple(o))

	return tree, env, stack

def std_string(item, tree, env, stack):
	o = list(item)
	o[0] = 'string'
	o[1] = ""
	stack.append(tuple(o))

	return tree, env, stack

def std_integer(item, tree, env, stack):
	o = list(item)
	o[0] = 'integer'
	o[1] = 0
	stack.append(tuple(o))

	return tree, env, stack

def std_float(item, tree, env, stack):
	o = list(item)
	o[0] = 'float'
	o[1] = 0.0
	stack.append(tuple(o))

	return tree, env, stack

def std_symbol(item, tree, env, stack):
	o = list(item)
	o[0] = 'symbol'
	o[1] = ""
	stack.append(tuple(o))

	return tree, env, stack

def std_source(item, tree, env, stack):
	o = list(item)
	o[0] = 'source'
	o[1] = []
	stack.append(tuple(o))

	return tree, env, stack

def std_not(item, tree, env, stack):
	# TODO

	return tree, env, stack

def std_if(item, tree, env, stack):
	conditional = list(stack.pop())
	if_truthy = list(stack.pop())
	if_falsey = False

	if stack[-1:] and stack[-1][0] == 'symbol' and stack[-1][1] == 'else':
		stack.pop()
		if_falsey = stack.pop()

	rstack = copy.deepcopy(stack)
	renv = copy.deepcopy(env)

	if not evaluate(conditional[1], renv, rstack):
		print("IF ERROR IN CONDITIONAL", conditional)
		# TODO Raise error
		return tree, env, stack

	ret = rstack.pop()
	if ret[1]:
		if if_truthy:
			if not evaluate(if_truthy[1], env, stack):
				print("IF ERROR ON TRUTHY", if_truthy)
				# TODO: Raise error
				return tree, env, stack
	else:
		if if_falsey:
			if not evaluate(if_falsey[1], env, stack):
				print("IF ERROR ON FALSEY", if_falsey)
				# TODO: Raise error
				return tree, env, stack

	return tree, env, stack

def std_while(item, tree, env, stack):
	conditional = list(stack.pop())
	if_truthy = list(stack.pop())

	rstack = copy.deepcopy(stack)
	renv = copy.deepcopy(env)

	while True:
		if not evaluate(conditional[1], renv, rstack):
			print("WHILE ERROR IN CONDITIONAL", conditional)
			# TODO: Raise error
			return tree, env, stack

		ret = rstack.pop()
		if ret[1]:
			if not evaluate(if_truthy[1], env, stack):
				print("WHILE ERROR IN BODY", if_truthy)
				# TODO: Raise error
				return tree, env, stack

			if stack[-1:] and stack[-1][0] == 'symbol' and stack[-1][1] == 'break':
				break
		else:
			break

	return tree, env, stack

def std_for(item, tree, env, stack):
	# TODO: for <symbol> in <block>
	# TODO: for <init_block> <cond_block> <body_block>

	return tree, env, stack

def stdlib():
	r = {}

	r['version'] = std_version

	r['add'] = std_add

	r['print'] = std_print
	
	r['type'] = std_type
	
	r['assign'] = std_assign
	
	r['begin'] = std_begin
	r['end'] = std_end
	r['drop'] = std_drop
	
	r['doc'] = std_doc
	r['help'] = std_help

	r['raise'] = std_raise

	r['load'] = std_load
	r['import'] = std_import
	r['export'] = std_export
	
	r['if'] = std_if
	
	r['equal'] = std_equal
	r['not'] = std_not

	r['while'] = std_while
	r['for'] = std_for

	r['block'] = std_block
	r['boolean'] = std_boolean
	r['string'] = std_string
	r['integer'] = std_integer
	r['float'] = std_float
	r['symbol'] = std_symbol
	r['source'] = std_source

	r['tosymbol'] = std_tosymbol
	r['toboolean'] = std_toboolean

	return r

def default_env():
	return [stdlib(), {"#MAIN#": ("boolean", "#MAIN#", True, -1, -1, -1, -1)}]

def evaluate(tree, env=None, stack=[]):
	if not env:
		env = default_env()
	else:
		env.append({})

	for item in tree:
		item_type = item[0]
		item_value = item[1]
		item_repr = item[2]
		item_begin_line = item[3]
		item_begin_char = item[4]
		item_end_line = item[5]
		item_end_char = item[6]
		if item_type == 'source':
			env.append({})
			if evaluate(item_value, env, stack):
				pass
			else:
				# TODO: Error
				print("Evaluate error", item)
				return False
		elif item_type == 'string':
			stack.append(item)
		elif item_type == 'boolean':
			stack.append(item)
		elif item_type == 'integer':
			stack.append(item)
		elif item_type == 'float':
			stack.append(item)
		elif item_type == 'block':
			stack.append(item)
		elif item_type == 'symbol':
			stack.append(item)
		elif item_type == 'null':
			stack.append(item)
		elif item_type == 'get':
			tree, env, stack = get(item, tree, env, stack)
		elif item_type == 'call':
			tree, env, stack = call(item, tree, env, stack)
		elif item_type == 'error':
			tree, env, stack = call(item, tree, env, stack)
		else:
			print("UNKNOWN TYPE", item)

	return True

def repl(env=None, stack=[]):
	if env == None:
		env = default_env()
	while True:
		line = input("> ")
		if line.strip():
			if not evaluate(loads(line), env, stack):
				print("EVAL FAIL", line)
				# TODO: Show error

def manual(section=None):
	section = section or 'table of contents'
	section_data = {}

	section_data['introduction'] = '\n\n'.join([
		"pallet is a highly flexible stack-oriented programming language.",
		"\tprint! \"Hello, World!\"",
		"The language is intended to be easily readable, easy for beginner programmers to learn, whilst simultaneously possessing fantastic metaprogramming abilities.",
		"Metaprogramming is something that tends to be reserved for either highly complicated languages, or for extremely complex interfaces. Yet, it is something a programmer may still find themself reaching for the moment they go off the beaten track.",
		"Creating something new shouldn't require strict discipline. It's an artform. Creativity should be allowed to flow freely.",
		"\tif! (equal? a b) {",
		"\t\tprint! \"True!\"",
		"\t} else {",
		"\t\tprint! \"False!\"",
		"\t}",
		"This little bit of code should feel mostly familiar. It feels a lot like many programming languages out there. However, the exact construction of this statement is actually wildly different.",
		"First, `if` is actually an ordinary function call. It is not a keyword or an inbuilt language construct. Which means it can be safely removed, if you feel the need. Or replaced, etc.",
		"Secondly, the bracketed sections are a type of list called a `block` by pallet. They're not statements. They're an ordinary list, which could be replaced by a variable reference - allowing you to manipulate the sections as you need.",
		"Thirdly, `else` is a `symbol` type. It is not a keyword. The `if` function checks the stack for it, which means you can conditionally generate an `else` if you want one.",
		"In short, everything you see above can be generated at runtime. Everything can be manipulated.",
		"\t= cond (equal? a b)",
		"\t(print! \"True!\"); = truthy",
		"\t= falsey (print! 'False!')",
		"\t= maybe `'else'",
		"\t= func if",
		"\t! $func $cond $truthy $maybe $falsey",
		"This little bit of code is exactly identical to the one from before. The only difference is, we're storing and calling our variables."
	])

	section_data['hello world'] = '\n\n'.join([
		"The famous 'Hello, World!' program is a simple program that can output a message to the screen.",
		"In pallet, it is as simple as you might expect:",
		"\tprint! 'Hello, World!'",
		"To break it down further, you push a string with your message to the stack, push the print symbol to the stack, and then call it from the environment:",
		"\t'Hello, World!'",
		"\tprint",
		"\tcall!",
		"In pallet, each line of a program is parsed from right-to-left, rather than the other way around. This is mostly because it's a stack-oriented language, but we still want it easily readable.",
		"To give another example:",
		"\tadd! 1 3",
		"This little program runs in this order:",
		"\t3",
		"\t1",
		"\tadd",
		"\tcall!",
		"Every item that isn't a call is pushed to the top of a list that we refer to as the `stack`. This list is then passed to the executing call to decide what, if anything, to do with it."
	])

	section_data['variables'] = '\n\n'.join([
		"Strictly speaking, variables don't exactly exist in pallet.",
		"Rather, when you use the `assign` function from the Standard Library, it generates a function that copies a value onto the `stack` when called.",
		"The `get` call simply runs that function, and if nothing was output, puts a `null` onto the stack instead.",
		"Thus, these two lines are very similar:",
		"\t$a",
		"\ta!",
		"There are two ways to do an assignment. Both call the `assign` function from the Standard Library, if it is available. (You can of course override the symbol in your environment.)",
		"\t= VariableName VariableValue",
		"\tassign! VariableName VariableValue",
		"The environment is scoped, with shadowing rather than overwriting. The `begin` function from the Standard Library appends a new environment table, and `end` removes it.",
		"\t= a 'Outer'",
		"\tbegin!",
		"\t\t= a 'Inner'",
		"\t\tprint! $a",
		"\tend!",
		"\tprint! $a",
		"Of course, if the variable is in the same environment as the new assignment, it is overwritten.",
		"\t= a 'Original'",
		"\t= a 'Overwritten'",
		"\tprint! $a"
	])

	toc = sorted([k for k in section_data])

	# Allow accessing by toc number:
	if section.isdigit():
		try:
			section = toc[int(section) - 1]
		except:
			pass

	# Generate TOC:
	section_data['table of contents'] = '\n\n'.join(["{}) {}".format(idx + 1, k.title()) for idx, k in enumerate(toc)])

	if section.lower().strip() != 'all':
		try:
			section_data[section.lower().strip()]
		except KeyError:
			section = 'table of contents'

		print("# pallet | " + section.title())
		print()
		print(section_data[section.lower().strip()])
	else:
		print("# pallet")
		print('A stack-oriented programming interpreter.')
		print()
		print('---')
		print()
		for section in toc:
			print("# pallet | " + section.title())
			print()
			print(section_data[section.lower().strip()])
			print()
			print('---')
			print()

		print("(c) James Milne")
		print()
		print()

	# TODO: provide a std_manual call, too.

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(
		description='A stack-oriented programming interpreter.',
		epilog='(c) James Milne')

	parser.add_argument('-f', '--file')
	parser.add_argument('-r', '--repl', action='store_true')
	parser.add_argument('-m', '--manual', action='store_true')
	parser.add_argument('-s', '--manual-section')

	args = parser.parse_args()

	if args.manual:
		manual(args.manual_section)
	else:
		if args.file:
			if not evaluate(load(args.file)):
				print("LOAD FAILED", args.file)
				# TODO: Raise error
		if args.repl or not args.file:
			repl()
