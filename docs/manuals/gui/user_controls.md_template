# Controls

Controls are user interface objects that are displayed on a given page,
representing some application data, and that users typically can
interact with. They can be directly created within the Markdown text (see the
[`Markdown`](../../reference/#taipy.gui.renderers.Markdown) class)
or HTML content (see the [`Html`](../../reference/#taipy.gui.renderers.Html) class).

!!! info "Every control that can be used in a page has a type, and a set of properties."

## Specific set of properties

Beside those common properties, every control type has a specific set of properties that you
can use, listed in the documentation page for that control type.

## Property value

Every property value can be set to a given value, that depends on the property type, or a
formatted string literal, also known as a `_f-string_`. This string may reference variable
names defined in your code, and the evaluated string is used as the property value.

!!! info "The property value is also updated when your Python variable is modified."

## Property name

Every control type has a default property name
If you want to set the value for this property,
you can use the short version of the control syntax.

## Syntax

Controls are declared in your page content using the Markdown or the HTML syntax.

### Markdown

Creating a control in Markdown text is just a matter of inserting a text
fragment.

```py
<|control_type|property_name=property_value|...|>
```

!!! info "You can have as many property name-property value pairs as needed, and where space characters _are_ significant."

!!! info "All controls have a `_default property_` that can be used before the control type to shorten the definition"

    ```py
    <|control_type|default_property_name=default_property_value|>
    ```

    Is equivalent to

    ```py
    <|default_property_value|control_type|>
    ```

Please refer to the [Markdown syntax in Pages](user_pages.md#markdown-specifics) for all the details
on the Taipy Markdown extension syntax.

### HTML

If you choose to embed Taipy controls into existing HTML pages, you can use the following
syntax:

```html
<taipy:control_type property_name="property_value" ...> </taipy:control_type>
```

The text element of the control tag can be used to indicate the default property value:

```html
<taipy:control_type default_property_name="default_property_value" ... />
```

is equivalent to

```html
<taipy:control_type>default_property_value</taipy:control_type>
```

!!! info "HTML syntax extensions"

    The HTML text that is given to the [HTML](../../reference/#taipy.gui.renderers.Html)
    page renderer is actually not parsed as pure HTML. Instead, it is transformed before
    it is sent as HTML to be rendered. Therefore, Taipy was able to introduce a few changes
    to the pure HTML syntax that make it easier to use in the context of describing Taipy
    pages.

    - Attribute names that be array elements.
      Some controls (such as the [`chart`](controls/chart.md) control)needed indexed
      properties. An attribute name such as _y[1]_ is valid in the Taipy context,
      where it would not be elsewhere.

    - Empty attribute value.
      In the HTML used by Taipy, you can mention an attribute with no value. It would
      be equivalent to setting it to `True`.

## Generic properties

Every control type has the following properties:

-   `id`: The identifier of the control, generated in the HTML component.
-   `class_name`: An additional CSS class that is added to the generated HTML component.
    Note that all controls are generated with the "taipy-_control_type_" CSS class set (ie.
    the `button` control generates an HTML element that has the _taipy-button_ class).
-   `properties`: The name of a variable that holds a dictionary where all property name and
    value pairs will be used by a given control declaration.

All or most of the Taipy controls expose similar properties that can be user in generic
manner across your pages.

### The `_id_` property

You can specify an identifier for a specific control.

This identifier is used as the `id` attribute of the generated HTML component so you
can use it in your CSS selectors. This identifier is also sent to the _on_action_ function
of the `_Gui_` instance, if this control can trigger actions.

### The `_properties_` property

There are situations where your control may need a lot of different properties. This is
typically the case for complex controls like [_chart_](controls/chart.md) or
[_table_](controls/table.md).

Instead of having to list all the properties with their appropriate value, potentially
making the reading of the content difficult, you can create a Python dictionary, that
contains all the required key-value pair, and use the name of the variable that holds
that dictionary as the value of the _properties_ property.

!!! Example

    Say you Markdown content needs the following control:
    `<|dialog|title=Dialog Title|open={show_dialog}|page_id=page|validate_action=validate_action|cancel_action=cancel_action||validate_action_text=Validate|cancel_action_text=Cancel|>`

    You can argue that this is pretty long, and could be improved. In this situation, you might
    prefer to create a simple Python dictionary:

    ``` py linenums="1"

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
    ``` py
    <{show_dialog}|dialog|properties=dialog_props|>
    ```

### The _propagate_ property

If the _propagate_ property is set to `_True_`, then the application variable bound to a control
is updated when the user modifies the value represented by the control.

!!! info "Note that if there is a `_on_update_` function declared on the _Gui_ instance, it will be invoked as well."

## Controls list

Here is the list of all available controls in Taipy:

!!! abstract "TODO: Generate controls list"

[CONTROLS_LIST]
