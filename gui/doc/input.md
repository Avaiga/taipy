A control that displays some text that can potentially be edited.

## Styling

All the input controls are generated with the "taipy-input" CSS class. You can use this class
name to select the input controls on your page and apply style.

## Usage

### Get user input

You can create an input field bound to a variable with the following content:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|input|>
        ```
  
    === "HTML"

        ```html
        <taipy:input>{value}</taipy:input>
        ```

