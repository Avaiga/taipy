Displays its children in a block.

The `part` block is used to group visual elements in a single element.
This allows to show or hide them in one action and be placed as a unique element in a [`Layout`](layout.md) cell.

There is a simplified Markdown syntax to create a `part`, where the element name is optional:

`<|` just before the end of the line indicates the beginning of a `part` element;
`|>` at the beginning of a line indicated the end of the `part` definition.


## Styling

All the part blocks are generated with the "taipy-part" CSS class. You can use this class
name to select the part blocks on your page and apply style.

### [Stylekit](../styling/stylekit.md) support

The [Stylekit](../styling/stylekit.md) provides specific classes that you can use to style part
blocks:

- *align-item-top*<br/>
  If this part block is inside a [`layout`](layout.md) block, this CSS class aligns the part
  content to the top the layout column it belongs to.
- *align-item-center*<br/>
  If this part block is inside a [`layout`](layout.md) block, this CSS class vertically aligns
  the part content to the center of the layout column it belongs to.
- *align-item-bottom*<br/>
  If this part block is inside a [`layout`](layout.md) block, this CSS class vertically aligns
  the part content to the bottom of the layout column it belongs to.
- *align-item-stretch*<br/>
  If this part block is inside a [`layout`](layout.md) block, this CSS class 
  gives the part the same height as the highest item in the row where this part
  appears in the layout.

The Stylekit also has several classes that can be used to style part blocks,
as described in the [Styled Sections](../styling/stylekit.md#styled-sections)
documentation.<br/>
Because the default property of the *part* block is *class_name*, you can use the
Markdown short syntax for parts:

```
<|card|
...
  (card content)
...
|>
```

Creates a `part` that has the [*card*](../styling/stylekit.md#card) class defined
in the Stylekit.

## Usage

### Grouping controls

!!! example "Page content"

    === "Markdown"

        ```
        <|
        ...
        <|{Some Content}|>
        ...
        |>
        ```

    === "HTML"

        ```html
        <taipy:part>
        ...
        <taipy:text>{Some Content}</taipy:text>
        ...
        </taipy:part>
        ```

### Showing and hiding controls

!!! example "Page content"

    === "Markdown"

        ```
        <|part|don't render|
        ...
        <|{Some Content}|>
        ...
        |>
        ```

    === "HTML"

        ```html
        <taipy:part render="False">
            ...
            <taipy:text>{Some Content}</taipy:text>
            ...
        </taipy:part>
        ```

If the *render* property is bound to a Boolean value, the `part` will show or hide its elements according to the value of the bound variable.

### Styling parts

The default property name of the `part` block is *class_name*. This allows for setting
a CSS class to a `part` with a very simple Markdown syntax:

!!! example "Markdown content"

    ```
    <|css-class|
    ...
    (part content)
    ...
    |>
    ```

This creates a `part` block that is applied the *css-class* CSS class defined in the
application stylesheets.

### Part with page

The content of the part can be specified as an existing page name or an URL using the *page* property.

!!! example "Page content"

    === "Markdown"

        ```
        <|part|page=page_name|>
        ```

    === "HTML"

        ```html
        <taipy:part page="page_name"/>
        ```

### Part with partial

The content of the part can be specified as a `Partial^` instance using the *partial* property.

!!! example "Page content"

    === "Markdown"

        ```
        <|part|partial={partial}|>
        ```

    === "HTML"

        ```html
        <taipy:part partial="{partial}" />
        ```
