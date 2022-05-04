A control that can display and specify a formatted date, with or without time.

## Usage

### Using the full date and time

Assuming a variable _dt_ contains a Python `datetime` object, you can create
a date selector that represents it:

!!! example "Page content"

    === "Markdown"

        ```
        <|{dt}|date|>
        ```
  
    === "HTML"

        ```html
        <taipy:date>{dt}</taipy:date>
        ```

### Using only the date

If you don't need to use the date, you can do so:

!!! example "Page content"

    === "Markdown"

        ```
        <|{dt}|date|not with_time|>
        ```
  
    === "HTML"

        ```html
        <taipy:date with_time="false">{dt}</taipy:date>
        ```


