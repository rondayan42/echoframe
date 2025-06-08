# Rewritten Study Uplinks for Echoframe, now tailored for complete beginners
# Tone: lightly cynical, clear, detailed, and beginner-focused — with full syntax awareness

study_docs = {
    0: '''📖 Study Uplink: Echo 1

Let’s start with Python’s most basic spell: `print()`.
This function sends a message to the screen — literally prints it out.

Example:
    print("FREQ signal received")

👉 `print()` is a **function** — a reusable block of code that performs an action.
👉 The text you want to show must be in **quotation marks** — either double (`"`) or single (`'`), but not both at once.
👉 The content in quotes is a **string** — a piece of text. Strings are one of the core data types in Python.
👉 Python ends every instruction with a newline, not a semicolon (but you *can* use semicolons to put multiple statements on one line — don’t).

📌 Also: Python is case-sensitive. `Print()` won’t work. It’s `print()`, all lowercase.
''',

    1: '''📖 Study Uplink: Echo 1X

Same `print()` function, different mission: now you choose what to say.

Example:
    print("Echoframe initialized")

🧠 Extra syntax tips:
- A **statement** is a line of code that does something — like calling `print()`.
- Python reads and runs your code line-by-line from top to bottom. The order *always* matters.
- You can put a comment at the end of a line using `#`, and Python will ignore it.

Example:
    print("hello")  # this prints the word hello
''',

    2: '''📖 Study Uplink: Echo 2

Variables store values. Think of them like memory slots with names.

Example:
    core = "Echoframe"

👉 The `=` symbol is the **assignment operator**. It doesn’t mean “equals” — it means “take what’s on the right and put it into the name on the left.”
👉 Variable names must start with a letter or underscore and can’t contain spaces or symbols like `!` or `-`.
👉 Python doesn’t require you to declare the variable type — it figures it out from context. This is called **dynamic typing**.

Example:
    thing = 5      # this is an integer
    thing = "5"    # now it's a string
''',

    3: '''📖 Study Uplink: Echo 2X

You can create multiple variables and use them later.

Example:
    op1 = "Ping"
    op2 = "Trace"
    op3 = "Relay"
    print(op2)

💡 A variable can hold any kind of data: string, number, list, even another function.
And once you assign it, you can overwrite it anytime:
    op2 = "Hacked"
That’s it — Python will replace the old value silently. No warnings.
''',

    4: '''📖 Study Uplink: Echo 3

`for` loops repeat something for each item in a sequence.

Example:
    for i in range(3):
        print(i)

🔍 Syntax rules:
- `for` and `in` are **keywords** — special words that Python recognizes.
- The loop line ends with a colon (`:`).
- The block underneath must be **indented** — usually 4 spaces or a tab.

⚠️ Forgetting the colon or indentation = syntax error.

Also: `range(3)` gives 0, 1, 2 — **not** 3. Python is exclusive on the end.
''',

    5: '''📖 Study Uplink: Echo 3X

You can count backward or skip numbers using this format:

Example:
    for i in range(3, 0, -1):
        print(i)

Syntax:
    range(start, stop_before, step)

✅ The third argument is the **step** — how much to add (or subtract) each time.

🔁 A negative step counts down. A positive one counts up.
''',

    6: '''📖 Study Uplink: Echo 4

Control flow — making decisions with `if`, `else`, and friends.

Example:
    user = "admin"
    if user == "admin":
        auth = "Access Granted"
    else:
        auth = "Access Denied"

Syntax breakdown:
- `==` checks equality
- `:` is required after `if` and `else`
- Blocks must be indented beneath them

🧠 You can also use `elif` for more than two choices:
    if condition1:
        ...
    elif condition2:
        ...
    else:
        ...
''',

    7: '''📖 Study Uplink: Echo 4X

Just like before, but this time you also print the result.

Example:
    rank = "technician"
    if rank == "admin":
        access = "full"
    else:
        access = "limited"

    print(access)

❗ Variables created inside `if` blocks still exist afterward — Python scopes them loosely in this case.
''',

    8: '''📖 Study Uplink: Echo 5

Functions let you group code into reusable chunks.

Example:
    def transmit():
        return "Signal Clear"

    status = transmit()

Syntax checklist:
- `def` starts a function definition
- Function names use `snake_case`
- Parentheses `()` are required even if there are no inputs
- `return` sends a result back from the function

You can call the function later using its name followed by parentheses.
''',

    9: '''📖 Study Uplink: Echo 5X

Multiple functions, only one gets used.

Example:
    def ping():
        return "beep"

    def pong():
        return "boop"

    signal = pong()

✅ Python ignores unused functions unless called.
Pro tip: Functions must be defined before they’re called — top to bottom still applies.
''',

    10: '''📖 Study Uplink: Echo 6

Lists are collections of items. They're ordered and mutable.

Example:
    nodes = [1, 2, 3]
    print(nodes)

Syntax:
- Square brackets `[ ]` define the list
- Items are separated by commas
- You can access items with `nodes[0]`, `nodes[1]`, etc.
''',

    11: '''📖 Study Uplink: Echo 6X

To add something to a list, use `.append()`:

Example:
    nodes = [1, 2, 3]
    nodes.append(4)
    print(nodes)

✅ This modifies the original list. It doesn’t return a new one.
''',

    12: '''📖 Study Uplink: Echo 7

Dictionaries (aka dicts) store key-value pairs.

Example:
    cipher = {'a': 1, 'b': 2}
    decoded = cipher['a']

Syntax:
- Keys are separated from values by colons (`:`)
- Pairs are separated by commas
- Access with `dict[key]`
''',

    13: '''📖 Study Uplink: Echo 7X

Dictionaries are mutable — you can change them after creation.

Example:
    cipher = {'a': 1, 'b': 2}
    cipher['b'] = 9
    mod = cipher['b']
''',

    14: '''📖 Study Uplink: Echo 8

Want to combine values from a list? Use a **loop** and a **total**.

Example:
    total = 0
    for i in [1, 2, 3]:
        total += i

This is called **accumulation**.
''',

    15: '''📖 Study Uplink: Echo 8X

Raise numbers to powers using `**`.

Example:
    total = 0
    for i in [1, 2, 3]:
        total += i ** 2

`i ** 2` is i squared. Replace `2` with any number to raise it to a higher power.

🧮 Bonus — other numeric operators you’ll see a lot:
- `+`  (addition): `a + b`
- `-`  (subtraction): `a - b`
- `*`  (multiplication): `a * b`
- `/`  (division, always gives float): `a / b`
- `//` (floor division — rounds down): `a // b`
- `%`  (modulo — gives the remainder): `a % b`

These can all be used with variables too, like:
    a = 5
    b = 2
    print(a % b)  # prints 1

You can combine them with assignment just like `+=`:
- `-=`, `*=`, `/=`, `//=`, and so on.
''',

    16: '''📖 Study Uplink: Echo 9

`while` loops repeat code until a condition is false.

Example:
    i = 1
    while i <= 3:
        print(i)
        i += 1

⚠️ If you forget to update the condition, the loop runs forever.
''',

    17: '''📖 Study Uplink: Echo 9X

Control your loop step manually:

Example:
    i = 2
    while i <= 6:
        print(i)
        i += 2
''',

    18: '''📖 Study Uplink: Echo 10

You can capture return values from functions instead of printing them.

Example:
    def identify():
        return "Code Complete"

    flag = identify()
''',

    19: '''📖 Study Uplink: Echo 10X

Use **f-strings** to inject variables into text.

Example:
    def welcome(name):
        return f"Welcome, {name}"

    flag = welcome("Ron")

📎 `f"..."` is a format string. Anything inside `{}` gets evaluated.
🛑 Don’t forget the `f` at the beginning.
'''
}

