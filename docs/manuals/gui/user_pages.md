# Pages

Pages are the base for your user interface. Pages hold text, images and controls that
display information that the application needs to publish, and ways to interact with
the application data.

## Page renderers

Taipy lets you create as many pages as you want, with whatever content you need.
Pages are created using `_page renderers_`, that convert some text (inside the application
code or from an external file) into HTML content that is sent and rendered onto the client
device.

!!! info "A `_page rendered_` is a Python class that reads some text (directly from a string, or reading a text file) and converts it into a page that can be displayed in a browser."

There are different types of page renderers in Taipy but all follow the same core
principles: they parse some input text, locate the Taipy-specific constructs that
involve, in the case of Taipy controls, the creation of potentially complex HTML
components, bind these controls to application variables and connect `_callbacks_`
from the rendered page back to the Python code, if you want to watch user events
(the notion of callbacks is detailed in the section [Callbacks](user_callbacks.md)).

### Registering the page

Once you have created an instance of a page renderer for a specified piece of
text, you can register that page to the [`Gui`](../reference/#taipy.gui.gui.Gui) instance
used by your application.

### Viewing the page

When the user browser connects to the Web server, requesting the indicated page,
the rendering takes place (involving the retrieval of the application variable
values) and you can see your application's state, and interact with it.

### Python markdown

Taipy uses [Python Markdown](https://python-markdown.github.io/) to translate Markdown
text to elements that are used to create Web pages. It also uses many extensions that
make it easier to create nice-looking page that user can enjoy. Specifically,
Taipy uses the following extensions: `_admonition_`, `_attr_list_`, `_fenced_code_`, `_meta_`, `_md_in_html_`, `_sane_lists_` and `_tables_`. Please refer to the Python Markdown package documentation to get information on how these are used.

### Markdown specifics

Beside these extension, Taipy adds its own, that can parse a Taipy-specific
construct that allows for defining controls (and all the properties they need)
and structuring elements.

!!! info "The basic syntax for creating Taipy constructs in Markdown is: `_<|...|...|>_`. Taipy will interpret any text between the `_<|_ and the _|>_` markers and try to make sense of it."

The most common use is to create controls. Taipy expects the control type name
to appear as the first `_|...|_` element.

!!! info "If it fails to do so, Taipy will consider the first element to be the default value for the default property of the control, whose name must then appear as the second element."

Every following elements will be interpreted as a property name-property value pair
using the syntax: `_property_name_=_property_value_` (note that all space characters
are significative).  
Should the `_=property_value_` fragment be missing, the property value is interpreted
as the Boolean value `True`.

!!! info "If the property name is preceded by the text "_no _", "_not _", "_don't _" or "_dont _" (including the trailing space character) then no property value is expected, and the property value is set to `False`."

#### Some examples

!!! example "Multiple properties"

    You can have several properties defined in the same control fragment:
    ``` py
    _<|button|label=Do something|active=True|>_

    ```

!!! example "The _default property_ rule"

    The control type [`button`](controls/button.md) has a default property called _label_. In Taipy, the Markdown text

    ``` py

    _<|button|label=Some text|>_

    ```

    Is exactly equivalent to

    ``` py

    _<|Some text|button|>_

    ```

!!! example "The _missing Boolean property value_ rules"

    ``` py

    _<|button|active=True|>_

    ```

    Is equivalent to

    ``` py

    _<|button|active|>_

    ```

    And

    ``` py

    _<|button|active=False|>_

    ```

    Is equivalent to

    ``` py

    _<|button|not active|>_

    ```

There are a very few exceptions to the _<|control_type|>_ syntax, that are described
in their respective documentation section. The most obvious exception being the
[`field`](controls/field.md) control, that can be created without even mentioning it's
type.

### HTML specifics

!!! abstract "TODO: HTML specifics documentation"

## Root page

!!! abstract "TODO: root page documentation"

## Partials

There are page fragments that you may want to repeat on different pages. In that situation
you will want to use the `Partials` concept described below. This will avoid
repeating yourself when creating your user interfaces.

!!! abstract "TODO: partials documentation"

## Dialogs

Application sometimes need to prompt the user to indicate a situation or request an
input of some sort. This need is covered in Taipy using the [dialog](user_dialogs.md)
control that is demonstrated below.

!!! abstract "TODO: dialogs documentation"

## Panes

Modern user interface also provide small pages that pop out and be removed, for
temporary use such as providing specific parameters for the application. Taipy lets
you create such elements as described below.

!!! abstract "TODO: panes documentation"

## Local resources

!!! abstract "TODO: local ressources documentation"