#Callbacks

Callbacks are functions that you create in your application, that are meant to be
invoked in response to user actions in generated pages, or other events that the
Web browser requires that the application takes care of.

## Variable value change

Some controls (such as [`input`](viselements/input.md) or [`slider`](viselements/slider.md))
let the user modify the value they hold.  
Because you may want to control what that _new value_ is, and decide whether to use
as such or not, a callback function is called in your application when the user
activates the control so as to change its value.

!!! example

    ``` py linenums="1"
    from taipy.gui import Gui

    md = """
    # Hello Taipy

    The variable `x` is here: <|{x}|slider|>.
    """

    x = 50

    def on_change(gui, var, val):
        if var == "x":
            print(f"'x' was changed to: {x}")

    Gui(page=md).run()
    ```

Once in your function body, you can check the new value for the variable, and decide
what to do with it: maybe you will need to trigger some other code to propagate the
side effects of the variable value being changed.

If you need to reset the value displayed at this moment, you can simply
change the variable value, assuming you use the `gui.` (or any other variable name you have
set the `Gui` instance to) prefix when referring to that variable. In our example, that would
be `gui.x`.

## Actions

Controls like buttons don't notify of any value change. Instead, they use _callbacks_ to let
the application knows that the user activated them somehow.

!!! example
    ``` py linenums="1"
    from taipy.gui import Gui

    md = """
    # Hello Taipy

    Press <|THIS|button|> button.
    """

    def on_action(gui, id, action):
        print("The button was pressed!")

    Gui(page=md).run()
    ```

The default behavior for these controls is to call the `on_action` function within your code,
if there is one.
