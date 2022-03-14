A side pane.

Pane allows to show some content on top of the current page.
The pane is closed when the user clicks outside the area of the pane (triggering a _on_close_ action).

## Usage

### Showing or hiding a pane

The default property, _open_, indicates whether the pane is visible or not:

!!! example "Page content"

    === "Markdown"

        ```
        <|{show}|pane|>
        ```
  
    === "HTML"

        ```html
        <taipy:pane>{show}</taipy:pane>
        ```

### Choosing where the pane appears

The _anchor_ property defines on which side of the display the pane is shown.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show}|pane|anchor=left|>
        ```
  
    === "HTML"

        ```html
        <taipy:pane anchor="left">{show}</taipy:pane>
        ```

### Showing the pane beside the page content

The pane is shown beside the page content instead of over it if the _persistent_ property evaluates to True.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show}|pane|persistent|>
        ```
  
    === "HTML"

        ```html
        <taipy:pane persistent="True">{show}</taipy:pane>
        ```

### Pane as block element

The content of the pane can be specified directly inside the pane block.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show}|pane|
            ...
            <|{some content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:pane open={show}>
            ...
            <taipy:text>{some content}</taipy:text>
            ...
        </taipy:pane>
        ```

### Pane with page

The content of the pane can be specified as an existing page name using the _page_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show}|pane|page=page_name|>
        ```
  
    === "HTML"

        ```html
        <taipy:pane page="page_name">{show}</taipy:pane>
        ```

### Pane with partial

The content of the pane can be specified as a `Partial^` instance using the _partial_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show}|pane|partial={partial}|>
        ```
  
    === "HTML"

        ```html
        <taipy:pane partial="{partial}">{show}</taipy:pane>
        ```
