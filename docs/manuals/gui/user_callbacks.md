#Callbacks

Callbacks are functions that you create in your application, that are meant to be
invoked in response to user actions in generated pages, or other events that the
Web browser requires that the application takes care of.

## Variable change

Some controls (such as [`input`](controls/input.md) or [`slider`](controls/slider.md))
let the user modify the value they hold.  
Because you may want to control what that _new value_ is, and decide whether to use
as such or not, a callback function is called in your application.

!!! example

    ``` py linenums="1"
    from taipy.gui import Gui, Markdown

    page = """
    # Hello Taipy

    The variable `x` is here: <|{x}|slider|>.
    """

    x = 50

    def on_value_change(gui, var, val):
        if var == "x":
            print(f"X was changed to: {x}")

    gui = Gui(page=Markdown(page))
    gui.on_update(on_value_change)
    if __name__ == '__main__':
        gui.run()
    ```

    Note how, in line 16, we indicate that the function `on_value_change` should be called when variables are modified.

Once if your function body, you can check the new variable value, and decide what to
do with it (may be trigger some other code that might be impacted by the variable
value change).

If you need to reset the value displayed at this moment, you can simply
change the variable value, assuming you use the `gui.` (or any other variable name you have
set the `Gui` instance to) prefix when referring to that variable. In our example, that would
be `gui.x`.

## Actions

Controls like buttons don't notify of a value change. Instead, they use _callbacks_ to let
the application know that they were activated.

!!! example
    ``` py linenums="1"
    from taipy.gui import Gui, Markdown

    page = """
    # Hello Taipy

    Press <|THIS|button|> button.
    """

    def on_action(gui, id, action):
        print("The button was pressed!")

    gui = Gui(page=Markdown(page))
    gui.on_action(on_action)
    if __name__ == '__main__':
        gui.run()
    ```

    Line 13 makes sure that the function `on_action` gets called when the user triggers an action on a control.
