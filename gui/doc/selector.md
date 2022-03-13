A control that allows for selecting items from a list of choices.

Each item is represented by a string, an image or both.

The selector can let the user select multiple items.

A filtering feature is available to display only a subset of the items.

You can use an arbitrary type for all the items (see the [example](#binding-to-a-list-of-objects)).

## Usage

### Display a list of string

You can create a selector on a series of strings:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|selector|lov=Item 1;Item 2;Item 3|>
        ```
  
    === "HTML"

        ```html
        <taipy:selector lov="Item 1;Item 2;Item 3">{value}</taipy:selector>
        ```

### Display as a dropdown

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|selector|lov=Item 1;Item 2;Item 3|dropdown|>
        ```
  
    === "HTML"

        ```html
        <taipy:selector lov="Item 1;Item 2;Item 3" dropdown="True">{value}</taipy:selector>
        ```


### Display with filter and multiple selection

You can add a filter input field that lets you display only strings that match the filter value.

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|selector|lov=Item 1;Item 2;Item 3|multiple|filter|>
        ```
  
    === "HTML"

        ```html
        <taipy:selector lov="Item 1;Item 2;Item 3" multiple="True" filter="True">{value}</taipy:selector>
        ```


### Display a list of tuples

A selector control that returns an id while selecting a label or Icon^.

!!! example "Page content"

    === "Markdown"

        ```
        <|{sel}|selector|lov={[("id1", "Label 1"), ("id2", Icon("/images/icon.png", "Label 2"),("id3", "Label 3")]}|>
        ```
  
    === "HTML"

        ```html
        <taipy:selector value="{sel}" lov="{[('id1', 'Label 1'), ('id2', Icon('/images/icon.png', 'Label 2'),('id3', 'Label 3')]}" />
        ```

### Display a list of objects

Assuming your Python code has created a list of object:
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

If you want to create a selector control that lets you pick a specific user, you
can use the following fragment.

!!! example "Page content"

    === "Markdown"

        ```
        <|{user_sel}|selector|lov={users}|type=User|adapter=lambda u: (u.id, u.name)|>
        ```
  
    === "HTML"

        ```html
        <taipy:selector lov="{users}" type="User" adapter="lambda u: (u.id, u.name)">{user_sel}</taipy:selector>
        ```

In this example, we are using the Python list _users_ as the selector's _list of values_.
Because the control needs a way to convert the list items (which are instances of the class
_User_) into a string that can be displayed, we are using an _adapter_: a function that converts
an object, whose type must be provided to the _type_ property, to a tuple. The first element
of the tuple is used to reference the selection (therefore those elements should be unique
among all the items) and the second element is the string that turns out to be displayed.
