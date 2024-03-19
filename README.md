# PyProps
*Version 1.2*

A Python based toolkit for proposition logic.

## Setup
**NOTE: your OS needs Graphviz backend installed for the visualizer to work.** If you use macOS, this can be done by `brew install graphviz`; if you use Windows, this can be done by `winget install graphviz`.


For Linux/macOS/POSIX, run the following in the source directory:
```sh
python -m venv ./venv  # create a virtual environment
source ./venv/bin/activate  # activate venv
pip install -r requirements.txt  # install dependencies
```

For Windows, run the following in the source directory:
```powershell
python -m venv ./venv  # create a virtual environment
.\venv\Scripts\Activate.ps1  # activate venv
pip install -r requirements.txt  # install dependencies
```


## Usage (Python)
Some basic usages below. More examples in `example_usage.py`.
```py
from pyprops import *
from pyprops_parser import *

# creating the formula "p IMPLIES q"
# creating manually
f = ImpliesFormula(NotFormula(PropVar('p')), PropVar('q'))

# using the parser
f = parse_formula('p IMPLIES q')

# comparing equations
g = parse_formula('NOT(p) or Q')
print(equivalent(f, g))  # True - these formulas are equivalent
print(f == g)  # False - this compares f.to_text() with g.to_text()

# converting into normal forms
f_cnf = c.to_cnf()  # convert to conjunctive normal form
print(f_cnf)  # automatically converted into str representation

# evaluate under a truth assignment
print(f.evaluate({'p': True, 'q': False}))  # False
print(f.evaluate({'p': False, 'q': False}))  # True
```

### Formula Format
The supported connectives are: `NOT`, `AND`, `OR`, `IMPLIES` and `IFF`. The program is case-sensitive, so the connectives have to be uppercased. Propositional variable names are aslo case-sensitive, they cannot contain spaces and should not be too long.

Always use brackets for nested equations (i.e. `p OR (q IMPLIES r)` rather than `p OR q IMPLIES r`), and note that, always use brackets with the connective `NOT`, even if that is for a single propositional variable (i.e. `NOT p` is not valid, use `NOT(p)` instead).

Different connectives within the same level is not valid, that is, `p AND q AND r` is valid but `p AND q OR r` is not, use `p AND (p OR r)` instead.

### Truth Assignments
Truth assignments are dictionaries with the variable names (as `str`) as keys and the value is either a `bool` or a `int` (`0` for `False` and anything else for `True`).

For example: `{'p': True, 'q': False}`

Using `formula.evaluate(truth_assignment)` will return a `bool` value that represents the truth of the formula under this truth assignment. It will raise a `ValueError` if the truth assignment does not include all propositional variables in the formula (having extra variables in a truth assignment is fine, they will simply be ignored).


## Usage (GUI)
Launch the visualizer:
```sh
python pyprops_visualizer.py
```
The format for the formula in the textbox is the same as described about.

However, note that **the truth assignment should be written in json format rather than Python `dict`**, that is: `{"p": true, "q": true}` rather than `{'p': True, 'q': True}` (double quotation marks are necessary, and booleans are lowercased).

If the truth assignment textbox is empty, then it will show a uncolored graph; if a valid truth assignment is given, a color coded graph is displayed with subformulas that evaluates to `True` displayed in green and subformulas that evaluates to `False` in red.

Other buttons do literally what they say.

Our visualizer is still in very early stage and only contains some basic functions, and it has problems such as not handling errors well and resizing window masses up aspect ratio of the visualized graph. We are planning to improve it later but we are all new to making GUI and we weren't able to finish these before the project deadline. Sorry about that.
