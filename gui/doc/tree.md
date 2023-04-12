A control that allows for selecting items from a hierarchical view of items.

Each item is represented by a string, an image or both.

The tree can let the user select multiple items.

A filtering feature is available to display only a subset of the items.

You can use an arbitrary type for all the items (see the [example](#binding-to-a-list-of-objects)).


## Styling

All the tree controls are generated with the "taipy-tree" CSS class. You can use this class
name to select the tree controls on your page and apply style.

## Usage

### Display a list of string

You can create a tree on a series of strings:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|tree|lov=Item 1;Item 2;Item 3|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree lov="Item 1;Item 2;Item 3">{value}</taipy:tree>
        ```

### Display with filter and multiple selection

You can add a filter input field that lets you display only strings that match the filter value.

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|tree|lov=Item 1;Item 2;Item 3|multiple|filter|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree lov="Item 1;Item 2;Item 3" multiple="True" filter="True">{value}</taipy:tree>
        ```


### Display a list of tuples

A tree control that returns an id while selecting a label or `Icon^`.

!!! example "Page content"

    === "Markdown"

        ```
        <|{sel}|tree|lov={[("id1", "Label 1", [("id1.1", "Label 1.1"), ("id1.2", "Label 1.2")]), ("id2", Icon("/images/icon.png", "Label 2")), ("id3", "Label 3", [("id3.1", "Label 3.1"), ("id3.2", "Label 3.2")])]}|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree value="{sel}" lov="{[('id1', 'Label 1'), ('id2', Icon('/images/icon.png', 'Label 2'),('id3', 'Label 3')]}" />
        ```

### Display with filter and multiple selection

You can add a filter input field that lets you display only strings that match the filter value.

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|tree|lov=Item 1;Item 2;Item 3|multiple|filter|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree lov="Item 1;Item 2;Item 3" multiple="True" filter="True">{value}</taipy:tree>
        ```


### Manage expanded nodes

The property _expanded_ must be used to control the expanded/collapse state of the nodes.
By default, the user can expand or collapse nodes.
If _expanded_ is set to False, there can be only one expanded node at any given level of the tree: 
if a node is expanded at a certain level and the user click on another node at the same level, the first node will be automatically collapsed.

The _expanded_ property can also hold a list of ids that are expanded.

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|tree|lov=Item 1;Item 2;Item 3|not expanded|>

        <|{value}|tree|lov=Item 1;Item 2;Item 3|expanded=Item 2|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree value="{value}" lov="Item 1;Item 2;Item 3" expanded="False" />

        <taipy:tree value="{value}" lov="Item 1;Item 2;Item 3" expanded="Item 2" />
        ```


### Display a list of objects

Assuming your Python code has created a list of object:
```py3
class User:
    def __init__(self, id, name, birth_year, children):
        self.id, self.name, self.birth_year, self.children = (id, name, birth_year, children)

users = [
    User(231, "Johanna", 1987, [User(231.1, "Johanna's son", 2006, [])]),
    User(125, "John", 1979, []),
    User(4,   "Peter", 1968, []),
    User(31,  "Mary", 1974, [])
    ]

user_sel = users[2]
```

If you want to create a tree control that lets you pick a specific user, you
can use the following fragment.

!!! example "Page content"

    === "Markdown"

        ```
        <|{user_sel}|tree|lov={users}|type=User|adapter={lambda u: (u.id, u.name, u.children)}|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree lov="{users}" type="User" adapter="{lambda u: (u.id, u.name, u.children)}">{user_sel}</taipy:tree>
        ```

In this example, we are using the Python list _users_ as the tree's _list of values_.
Because the control needs a way to convert the list items (which are instances of the class
_User_) into a string that can be displayed, we are using an _adapter_: a function that converts
an object, whose type must be provided to the _type_ property, to a tuple. The first element
of the tuple is used to reference the selection (therefore those elements should be unique
among all the items) and the second element is the string that turns out to be displayed.


### Display a list of objects with built-in adapter

Objects with attributes _id_, _label_ and _children_ (as a list) can de dealt directly by the built-in _lov_ adapter.

Assuming your Python code has created a list of object:
```py3
class User:
    def __init__(self, id, label, birth_year, children):
        self.id, self.label, self.birth_year, self.children = (id, label, birth_year, children)

users = [
    User(231, "Johanna", 1987, [User(231.1, "Johanna's son", 2006, [])]),
    User(125, "John", 1979, []),
    User(4,   "Peter", 1968, []),
    User(31,  "Mary", 1974, [])
    ]

user_sel = users[2]
```

If you want to create a tree control that lets you pick a specific user, you
can use the following fragment.

!!! example "Page content"

    === "Markdown"

        ```
        <|{user_sel}|tree|lov={users}|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree lov="{users}" value="{user_sel}" />
        ```

### Display a list of dictionary with built-in adapter

Dictionaries with keys _id_, _label_ and _children_ (as a list) can de dealt directly by the built-in _lov_ adapter.

Assuming your Python code has created a list of object:
```py3
users = [
    {"id": "231", "label": "Johanna", "year": 1987, "children": [{"id": "231.1", "label": "Johanna's son", "year": 2006}]},
    {"id": "125", "label": "John", "year": 1979, "children": []},
    {"id": "4", "label": "Peter", "year": 1968, "children": []},
    {"id": "31", "label": "Mary", "year": 1974, "children": []}
    ]

user_sel = users[2]
```
Displaying the data would be as simple as:

!!! example "Page content"

    === "Markdown"

        ```
        <|{user_sel}|tree|lov={users}|>
        ```
  
    === "HTML"

        ```html
        <taipy:tree lov="{users}" value="{user_sel}" />
        ```

