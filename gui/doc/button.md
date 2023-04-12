A control that can trigger a function when pressed.

## Styling

All the button controls are generated with the "taipy-button" CSS class. You can use this class
name to select the buttons on your page and apply style.

### [Stylekit](../styling/stylekit.md) support

The [Stylekit](../styling/stylekit.md) provides specific classes that you can use to style buttons:

* *secondary*<br/>*error*<br/>*warning*<br/>*success*<br/>
    Buttons are normally displayed using the value of the *color_primary* Stylekit variable.
    These classes can be used to change the color used to draw the button, respectively, with
    the *color_secondary*, *color_error*, *color_warning* and *color_success* Stylekit variable
    values.

    The Markdown content: 
    ```
    <|Error|button|class_name=error|><|Secondary|button|class_name=secondary|>
    ```

    Renders like this:
    <figure>
      <img src="../button-stylekit_color-d.png" class="visible-dark" />
      <img src="../button-stylekit_color-l.png" class="visible-light"/>
      <figcaption>Using color classes</figcaption>
    </figure>

* *plain*<br/>
    The button is filled with a plain color rather than just outlined.

    The Markdown content: 
    ```
    <|Button 1|button|><|Button 2|button|class_name=plain|>
    ```

    Renders like this:
    <figure>
        <img src="../button-stylekit_plain-d.png" class="visible-dark" />
        <img src="../button-stylekit_plain-l.png" class="visible-light"/>
        <figcaption>Using the <code>plain</code> class</figcaption>
    </figure>

* *fullwidth*: The button is rendered on its own line and expands across the entire available width.

## Usage

### Simple button

The button label, which is the button control's default property, is simply displayed as the button
text.

!!! example "Page content"

    === "Markdown"

        ```
        <|Button Label|button|>
        ```
  
    === "HTML"

        ```html
        <taipy:button>Button Label</taipy:button>
        ```

<figure>
    <img src="../button-simple-d.png" class="visible-dark" />
    <img src="../button-simple-l.png" class="visible-light"/>
    <figcaption>A simple button</figcaption>
</figure>

### Specific action callback

Button can specify a callback function to be invoked when the button is pressed.

!!! example "Page content"

    === "Markdown"

        ```
        <|Button Label|button|on_action=button_action_function_name|>
        ```

    === "HTML"

        ```html
        <taipy:button on_action="button_action_function_name">Button Label</taipy:button>
        ```

