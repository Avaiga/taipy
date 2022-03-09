Displays its child elements in a collapsable area.

Expandable is a block control.

## Usage

### Defining a title and managing expanded state

The default property _title_ defines the title shown when clthe visual element is collapsed.

!!! example "Page content"

    === "Markdown"

        ```
        <|Title|expandable|expand={expand}|>
        ```
  
    === "HTML"

        ```html
        <taipy:expandable expand="{expand}">Title</taipy:expandable>
        ```

### Content as block

The content of `expandable` can be specified as the block content.

!!! example "Page content"

    === "Markdown"

        ```
        <|Title|expandable|
            ...
            Some text
            ...
            <|{some content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:expandable.start>Title</taipy:expandable.start>
            ...
            Some text
            ...
            <taipy:text>{some content}</taipy:text>
            ...
        <taipy:expandable.end></taipy:expandable.end>
        ```
