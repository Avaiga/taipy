A modal dialog.

Dialog allows showing some content over the current page.
The dialog is closed when the user presses the Cancel or Validate buttons, or clicks outside the area of the dialog (triggering a Cancel action).

## Styling

All the dialogs are generated with the "taipy-dialog" CSS class. You can use this class
name to select the dialogs on your page and apply style.

## Usage

### Showing or hiding a dialog

The default property, _open_, indicates whether the dialog is visible or not:

!!! example "Page content"

    === "Markdown"

        ```
        <|{show_dialog}|dialog|on_action={lambda s: s.assign("show_dialog", False)}|>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog on_action="on_action={lambda s: s.assign('show_dialog', False)}">{show_dialog}</taipy:dialog>
        ```

With another action that would have previously shown the dialog with:

```py3
def button_action(state, id, action):
    state.show_dialog = True
```


### Specifying labels and actions

Several properties let you specify the buttons to show,
and the action (callback functions) triggered when buttons are pressed:

!!! example "Page content"

    === "Markdown"

        ```
        <|dialog|title=Dialog Title|open={show_dialog}|page_id=page1|on_action=dialog_action|labels=Validate;Cancel|>
        ```
  
    === "HTML"

        ```html
        <taipy:dialog
         title="Dialog Title"
         page_id="page1"
         labels="Validate;Cancel"
         on_action="dialog_action">{show_dialog}</taipy:dialog>
        ```

The implementation of the dialog callback could be:

```py3
def dialog_action(state, id, action, payload):
    with state as st:
        ...
        # depending on payload["args"][0]: -1 for close icon, 0 for Validate, 1 for Cancel
        ...
        st.show_dialog = False
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
