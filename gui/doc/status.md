Displays a status or a list of statuses.

## Details

Every status line has a message to be displayed and a status priority.

The status priority is defined by a string among "info" (or "i"), "success" (or "s"), "warning" (or "w"), and
"error" (or "e"). An unknown string value sets the priority to "info".<br/>
These priorities are sorted from lower to higher as indicated here.

The property [*value*](#p-value) can be set to a value with the following type:

- A tuple: the status shows a single line; the first element of the tuple defines the *status* value, and the second
  element holds the *message*.
- A dictionary: the status shows a single line; the key "status" of the dictionary holds the *status* value, and the
  key "message" holds the *message*.
- A list of tuples: a list of status entries, each defined as described above.
- A list of dictionaries: a list of status entries, each defined as described above.

When a list of statuses is provided, the status control can be expanded to show all individual
status entries. Users can then remove individual statuses if [*without_close*](#p-without_close)
is set to False (which is the default value).

## Styling

All the status controls are generated with the "taipy-status" CSS class. You can use this class
name to select the status controls on your page and apply style.

## Usage

### Show a simple status

To show a simple `status` control, you would define a Python variable:

```py
status = ("error", "An error has occurred.")
```

This variable can be used as the value of the property [*value*](#p-value) of
the `status` control:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|status|>
        ```
  
    === "HTML"

        ```html
        <taipy:status>{value}</taipy:status>
        ```

The control is displayed as follows:
<figure>
    <img src="../status-basic-d.png" class="visible-dark" />
    <img src="../status-basic-l.png" class="visible-light"/>
    <figcaption>A simple status</figcaption>
</figure>

Note that the variable *status* could have been defined as a dictionary to achieve the
same result:

```py
status = {
    "status": "error",
    "message": "An error has occurred."
}
```

### Show a list of statuses

The `status` control can show several status items. They are initially collapsed, where the
control shows the number of statuses with a status priority corresponding to the highest priority
in the status list.

You can create a list of status items as a Python variable:

```py
status = [
    ("warning", "Task is launched."),
    ("warning", "Taks is waiting."),
    ("error", "Task timeout."),
    ("info", "Process was cancelled.")
]
```

The declaration of the control remains the same:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|status|>
        ```
  
    === "HTML"

        ```html
        <taipy:status>{value}</taipy:status>
        ```

The control is initially displayed as this:
<figure>
    <img src="../status-multiple1-d.png" class="visible-dark" />
    <img src="../status-multiple1-l.png" class="visible-light"/>
    <figcaption>A collapsed status list</figcaption>
</figure>

If the user clicks on the arrow button, the status list is expanded:
<figure>
    <img src="../status-multiple2-d.png" class="visible-dark" />
    <img src="../status-multiple2-l.png" class="visible-light"/>
    <figcaption>An expanded status list</figcaption>
</figure>

The user can remove a status entry by clicking on the cross button. Here, the user
has removed the third status entry:
<figure>
    <img src="../status-multiple3-d.png" class="visible-dark" />
    <img src="../status-multiple3-l.png" class="visible-light"/>
    <figcaption>After the removal of a status</figcaption>
</figure>

### Prevent status dismissal

If you don't want the user to be allowed to dismiss the displayed statuses, you can set the *without_close* property to True:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|status|without_close|>
        ```
  
    === "HTML"

        ```html
        <taipy:status without_close="True">{value}</taipy:status>
        ```

With the same array as above, here is what the expanded control looks like:
<figure>
    <img src="../status-multiple4-d.png" class="visible-dark" />
    <img src="../status-multiple4-l.png" class="visible-light"/>
    <figcaption>Preventing removals</figcaption>
</figure>
