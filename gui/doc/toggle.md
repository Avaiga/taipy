A series of toggle buttons that the user can select.

## Details

Each button is represented by a string, an image or both.

You can use an arbitrary type for all the items (see the [example](#use-arbitrary-objects)).

## Styling

All the toggle controls are generated with the "taipy-toggle" CSS class. You can use this class
name to select the toggle controls on your page and apply style.

The [Stylekit](../styling/stylekit.md) also provides specific CSS classes that you can use to style
toggle controls:

- *relative*<br/>
  Resets the theme toggle position in the page flow (especially for the theme mode toggle).
- *nolabel*<br/>
  Hides the toggle control's label.

## Usage

### Display a list of string

You can create a list of toggle buttons from a series of strings:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|toggle|lov=Item 1;Item 2;Item 3|>
        ```
  
    === "HTML"

        ```html
        <taipy:toggle lov="Item 1;Item 2;Item 3">{value}</taipy:toggle>
        ```

### Unselect value

In a toggle control, all buttons might be unselected. Therefore there is no value selected.
In that case, the value of the property _unselected_value_ is assigned if specified.

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|toggle|lov=Item 1;Item 2;Item 3|unselected_value=No Value|>
        ```
  
    === "HTML"

        ```html
        <taipy:toggle lov="Item 1;Item 2;Item 3" unselected_value="No Value">{value}</taipy:toggle>
        ```

### Display a list of tuples

A toggle control that returns an id while selecting a label or `Icon^`.

!!! example "Page content"

    === "Markdown"

        ```
        <|{sel}|toggle|lov={[("id1", "Label 1"), ("id2", Icon("/images/icon.png", "Label 2"),("id3", "Label 3")]}|>
        ```
  
    === "HTML"

        ```html
        <taipy:toggle value="{sel}" lov="{[('id1', 'Label 1'), ('id2', Icon('/images/icon.png', 'Label 2'),('id3', 'Label 3')]}" />
        ```

### Use arbitrary objects

Assuming your Python code has created a list of objects:
```py3
class User:
    def __init__(self, id, name, birth_year):
        self.id, self.name, self.birth_year = (id, name, birth_year)

users = [
    User(231, "Johanna", 1987),
    User(125, "John", 1979),
    User(4,   "Peter", 1968),
    User(31,  "Mary", 1974)
    ]

user_sel = users[2]
```

If you want to create a toggle control that lets you pick a specific user, you
can use the following fragment:

!!! example "Page content"

    === "Markdown"

        ```
        <|{user_sel}|toggle|lov={users}|type=User|adapter={lambda u: (u.id, u.name)}|>
        ```
  
    === "HTML"

        ```html
        <taipy:toggle lov="{users}" type="User" adapter="{lambda u: (u.id, u.name)}">{user_sel}</taipy:toggle>
        ```

In this example, we are using the Python list _users_ as the toggle's _list of values_.
Because the control needs a way to convert the list items (which are instances of the class
_User_) into a string that can be displayed, we are using an _adapter_: a function that converts
an object, whose type must be provided to the _type_ property, to a tuple. The first element
of the tuple is used to reference the selection (therefore those elements should be unique
among all the items) and the second element is the string that turns out to be displayed.
