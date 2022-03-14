Displays a value as a static text.

Note that if order to create a `text` control, you don't need to specify the control name
in the text template. See the documentation for [Controls](../controls.md) for more details.

## Details

The _format_ property uses a format string like the ones used by the string _format()_ function of Python.

If the value is a `date` or a `datetime`, then _format_ can be set to a date/time formatting string.


## Usage

### Display value

You can represent a variable value as a simple, static text:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|>
        ```
  
    === "HTML"

        ```html
        <taipy:text>{value}</taipy:text>
        ```

### Formatted output

If your value is a floating point value, you can use the _format_ property
to indicate what the output format should be used.

To display a floating point value with two decimal place:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|text|format=%.2f|>
        ```

    === "HTML"

        ```html
        <taipy:text format="%.2f">{value}</taipy:text>
        ```
