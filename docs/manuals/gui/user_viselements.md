# Introduction to Visual Elements

_Visual Elements_ are user interface objects that are displayed on a given page.
Visual elements reflect some application data or give the page some structuring
or layout information. Most visual elements let users interact with the page content.

You create visual elements using a specific the Markdown syntax (see the
[`Markdown`](../../reference/#taipy.gui.renderers.Markdown) class)
or specific HTML tags (see the [`Html`](../../reference/#taipy.gui.renderers.Html) class).

## Properties

Every visual element that you can use in a page has a type and a set of properties.

Beside those common properties, every control type has a specific set of properties that you
can use, listed in the documentation page for that control type.

## Property value

Every property value can be set to a given value, that depends on the property type, or a
formatted string literal, also known as a _f-string_. This string may reference variable
names defined in your code, and the evaluated string is used as the property value.

!!! info "The property value is also updated when your Python variable is modified."

## Property name

Every control type has a default property name
If you want to set the value for this property,
you can use the short version of the control syntax.

## Syntax

Visual Elements are declared in your page content using the Markdown or the HTML syntax.

### Markdown

Creating a visual element in Markdown text is just a matter of inserting a text
fragment.

```py
<|control_type|property_name=property_value|...|>
```

!!! note
    You can have as many property name-property value pairs as needed, and all the space characters
    of the property value part _are_ significant.

!!! note  "Default property"
    All visual elements have a _default property_ that can be used _before_ the
    visual element type name type in order
    to shorten the definition of the element content:
    ```
    <|visual_element_type|default_property_name=default_property_value|>
    ```
    Is equivalent to
    ```
    <|default_property_value|visual_element_type|>
    ```

Please refer to the section about [Markdown syntax](user_pages.md#markdown-specifics) for all the details
on the Taipy Markdown extension syntax.

### HTML

If you choose to embed Taipy visual elements into existing HTML pages, you can use the
following syntax:
```html
<taipy:visual_element_type property_name="property_value" ...> </visual_element_type>
```

The text element of the visual element tag can be used to indicate the default property
value for this visual element:
```html
<taipy:visual_element_type default_property_name="default_property_value" ... />
```
is equivalent to
```html
<taipy:visual_element_type>default_property_value</taipy:visual_element_type>
```

!!! info "HTML syntax extensions"

    The HTML text that is given to the [HTML](../../reference/#taipy.gui.renderers.Html)
    page renderer is **not** parsed as pure HTML. Instead, it is transformed before
    it is sent as HTML to be rendered. Therefore, Taipy was able to introduce a few changes
    to the pure HTML syntax that make it easier to use in the context of describing Taipy
    pages.

    - Attribute names that be array elements.
      Some visual elements (such as the [`chart`](viselements/chart.md) control) need
      indexed properties. An attribute name such as _y[1]_ is valid in the Taipy context,
      where it would not be in raw HTML.

    - Empty attribute value.
      In the HTML used by Taipy, you can mention an attribute with no value. It would
      be equivalent to setting it to `True`.

## Generic properties

Every visual element type has the following properties:

-   `id`: The identifier of the element, generated in the HTML component.
-   `class_name`: An additional CSS class that is added to the generated HTML component.
    Note that all visual element are generated with the "taipy-_visual_element_type_" CSS
    class set (ie. the `button` control generates an HTML element that has the
    _taipy-button_ CSS class).
-   `properties`: The name of a variable that holds a dictionary where all property
    name/value pairs will be used by a given visual element declaration.

All or most of the Taipy visual elements expose similar properties that can be used in a
generic manner across your pages.

### The `id` property

You can specify an identifier for a specific visual element.

This identifier is used as the `id` attribute of the generated HTML component so you
can use it in your CSS selectors.

!!! note "This identifier is also sent to the _on_action_ function of the `Gui` instance, if this visual element can trigger actions."

### The `properties` property

There are situations where your visual element may need a lot of different properties.
This is typically the case for complex visual elements like the
[`chart`](viselements/chart.md) or the [`table`](viselements/table.md) controls.

Instead of having to list all the properties with their appropriate value, potentially
making the reading of the content difficult, you can create a Python dictionary, that
contains all the required key-value pair, and use the name of the variable that holds
that dictionary as the value of the `properties` property.

!!! Example

    Say your Markdown content needs the following control:
    `<|dialog|title=Dialog Title|open={show_dialog}|page_id=page|validate_action=validate_action|cancel_action=cancel_action||validate_action_text=Validate|cancel_action_text=Cancel|>`

    You can argue that this is pretty long, and could be improved. In this situation, you might
    prefer to declare a simple Python dictionary in your code:

    ```py linenums="1"
    dialog_props = {
      "title":           "Dialog Title",
      "page_id":         "page",
      "validate_label":  "Validate",
      "validate_action": "validate_action",
      "cancel_label":    "Cancel",
      "cancel_action":   "cancel_action"
    }
    ```

    Then shorten your Markdown text with the following syntax:
    ```
    <{show_dialog}|dialog|properties=dialog_props|>
    ```

### The `propagate` property

If the `propagate` property is set to `True`, then the application variable bound to a
visual element is updated when the user modifies the value represented by the element.

!!! info
    Note that if there is a function called `on_change` declared on the `Gui` instance, it will be
    invoked no matter what the _propagate_ value is."
