Displays its child elements in a collapsable area.

Expandable is a block control.

## Styling

All the expandable blocks are generated with the "taipy-expandable" CSS class. You can use this class
name to select the expandable blocks on your page and apply style.

## Usage

### Defining a title and managing expanded state

The default property _title_ defines the title shown when the visual element is collapsed.

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
            <|{some content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:expandable title="Title">
            ...
            <taipy:text>{some content}</taipy:text>
            ...
        </taipy:expandable>
        ```

### Expandable with page

The content of the expandable can be specified as an existing page name using the _page_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|Title|expandable|page=page_name|>
        ```
  
    === "HTML"

        ```html
        <taipy:expandable page="page_name">Title</taipy:expandable>
        ```

### Expandable with partial

The content of the expandable can be specified as a `Partial^` instance using the _partial_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|Title|expandable|partial={partial}|>
        ```
  
    === "HTML"

        ```html
        <taipy:expandable partial="{partial}">Title</taipy:dialog>
        ```
