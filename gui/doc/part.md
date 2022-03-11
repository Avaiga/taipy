Displays its children in a block.

The Part control is used to group controls. 
This allows to show or hide them in one action and to display them in one Layout^ cell.
Part controls can be simplified by not specifying the part keyword.

## Usage

### Grouping controls

!!! example "Page content"

    === "Markdown"

        ```
        <|
            ...
            <|{Some Content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:part>
            ...
            <taipy:text>{Some Content}</taipy:text>
            ...
        </taipy:part>
        ```

### Showing/Hiding controls

!!! example "Page content"

    === "Markdown"

        ```
        <|part|don't render|
            ...
            <|{Some Content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:part render="False">
            ...
            <taipy:text>{Some Content}</taipy:text>
            ...
        </taipy:part>
        ```
