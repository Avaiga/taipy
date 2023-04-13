A side pane.

Pane allows showing some content on top of the current page.
The pane is closed when the user clicks outside the area of the pane (triggering a _on_close_ action).

Pane is a block control.

## Styling

All the pane blocks are generated with the "taipy-pane" CSS class. You can use this class
name to select the pane blocks on your page and apply style.

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

The parent element must have the *flex* display mode in CSS. To achieve this using
the Markdown syntax, you can leverage the
[*d-flex* class](../styling/stylekit.md#c-d-flex) provided in the
[Stylekit](../styling/stylekit.md).

Here is a full example of how to do this:

```py
from taipy.gui import Gui

show_pane=True

page="""
<|d-flex|
<|{show_pane}|pane|persistent|width=100px|
Pane content
|>
This button can be pressed to open the persistent pane:
<|Open|button|on_action={lambda s: s.assign("show_pane", True)}|>
|>
"""

Gui(page=page).run()
```

The pane is initially opened. If you close it, the bound variable *show_pane* is
updated (set to False).<br/>
Pressing the button sets the variable *show_pane* to True using a lambda callback, which
opens the pane again.

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
