#Binding variables

Sometimes, you will want to display information that comes from your application.

In order to do that, Taipy allows [Controls](user_controls.md) to relate
directly to your application variables, and display their values.

Consider the following application:

```py linenums="1"
from taipy.gui import Gui, Markdown

page = """
# Hello Taipy

The variable `x` contains the value <|{x}|>.
"""

x = 1234

gui = Gui(page=Markdown(page))
if __name__ == '__main__':
    gui.run()
```

When run, the root page displays the value of the variable _x_, from your code.

## Expressions

Actually, the values that you can use in controls can be far more useful than
raw variables. You can create complete expressions, just like you would use
in the _f-string_ feature available since Python 3.

In the code above, simply replace `<|{x}|>` by `<|{x*2}|>`, and you can see the
double of _x_ being displayed.

!!! Note
        You can of course create complete expressions such as `|{x} and {y}|` to concatenate
        two variable values, or whatever your imagination and application requirements are.

## Lambda expressions

Some control properties can be assigned lambda expression to simplify the
code.

!!! abstract "TODO: provide a simple example of a lambda expression usage"
