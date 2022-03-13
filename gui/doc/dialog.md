A modal dialog.

Dialog allows to show some content over the current page.
The dialog is closed when the user presses the Cancel or Validate buttons, or clicks outside the area of the dialog (triggering a Cancel action).

## Usage

### Showing or hiding a dialog

The default property, _open_, indicates whether the dialog is visible or not:

!!! example "Page content"

    === "Markdown"

        ```
        <|{show_dialog}|dialog|>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog>{show_dialog}</taipy:dialog>
        ```

### Specifying labels and actions

Several properties let you specify which label should be used for which button,
and what actions (callback functions) are triggered when buttons are pressed:

!!! example "Page content"

    === "Markdown"

        ```
        <|dialog|title=Dialog Title|open={show_dialog}|page_id=page1|on_validate=validate_action|on_cancel=cancel_action|validate_action_text=Validate|cancel_action_text=Cancel|>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog
         title="Dialog Title"
         page_id="page1"
         validate_label="Validate"
         on_validate="validate_action"
         cancel_label="Cancel"
         on_cancel="cancel_action">{show_dialog}</taipy:dialog>
        ```

### Dialog as block element

The content of the dialog can be specified directly inside the dialog block.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show_dialog}|dialog|
            ...
            <|{some content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog open={show_dialog}>
            ...
            <taipy:text>{some content}</taipy:text>
            ...
        </taipy:dialog>
        ```

### Dialog with page

The content of the dialog can be specified as an existing page name using the _page_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show_dialog}|dialog|page=page_name|>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog page="page_name">{show_dialog}</taipy:dialog>
        ```

### Dialog with partial

The content of the dialog can be specified as a `Partial^` instance using the _partial_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|{show_dialog}|dialog|partial={partial}|>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog partial="{partial}">{show_dialog}</taipy:dialog>
        ```
