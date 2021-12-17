# Binding variables

In the [Pages](user_pages.md) section, we explained how content was transformed into
pages that users can actually see.

Sometimes, you may want to display information that comes from your application.  
In order to do that, Taipy allows controls (see [Controls](controls.md)) to bond
directly to your application variables, and display their values.

Consider the following application:
```
from taipy.gui import Gui, Markdown

page = """
# Hello Taipy

The variable `x` contains the value <|{x}|>.
"""

x = 1234

gui = Gui(default_page_renderer=Markdown(page))
if __name__ == '__main__':
    gui.run()
```
When run, the root page displays the value of the variable _x_, from your code.

## Expressions

Actually, the values that you can use in controls can be far more useful than
raw variables. You can create complete expressions, just like you would use
in the f-string feature available since Python 3.

In the code above, simply replace `<|{x}|>` by `<|{x*2}|>`, and you can see the
value of _x_ being multiplied by 2 when displayed.

You can of course create complete expressions such as `|{x} and {y}|` to concatenate
two variable values, or whatever your imagination and application requirements are.

## Lambda expressions

Some control properties can be assigned lambda expression to simplify the
code. In this situation, you must make sure that the lambda expression parameters,
if there are any, are declared globally in your application. If you do not declare
those variables beforehand, Taipy will complain that they don't exist at run-time,
and your page generation will be missing your property value.

