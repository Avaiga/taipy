# Binding variables

Sometimes, you will want to display information that comes from your application.<br/>
To achieve this goal, Taipy allows [visual elements](user_viselements.md)
to relate directly to your application variables, display their values, and even
change those variable values.

Consider the following application:

```py linenums="1"
from taipy.gui import Gui

page = """
# Hello Taipy

The variable `x` contains the value <|{x}|>.
"""

x = 1234

gui = Gui(page)
if __name__ == '__main__':
    gui.run()
```

When this program runs (and a Web browser is directed to the running server), the
root page displays the value of the variable _x_, directly from your code.

## Expressions

Values that you can use in controls and blocks can be more than raw variable values.
You can create complete expressions, just like you would use
in the _f-string_ feature (available since Python 3).

In the code above, simply replace `<|{x}|>` by `<|{x*2}|>`, and the double of _x_
will be displayed in your page.

!!! Note
        You can create complex expressions such as `|{x} and {y}|` to concatenate
        two variable values, or whatever your imagination and application requirements are.

## Lambda expressions

Some control properties can be assigned lambda expression to simplify the
code.

!!! abstract "TODO: provide a simple example of a lambda expression usage"
