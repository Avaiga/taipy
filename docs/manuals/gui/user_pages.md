# Pages

Pages are the base for your user interface. Pages hold text, images and controls that
display information that the application needs to publish, and ways to interact with
the application data.

## Page renderers

Taipy lets you create as many pages as you want, with whatever content you need.
Pages are created using _page renderers_, that convert some text (inside the application
code or from an external file) into HTML content that is sent and rendered onto the client
device.

!!! note
    A _page rendered_ is an instance of a Python class that reads some text (directly from a
    string, or reading a text file) and converts it into a page that can be displayed in a browser.

There are different types of page renderers in Taipy and all process their input text
with the following steps:

- The text is parsed in order to locate the Taipy-specific constructs. Those constructs
  may be _controls_ or _blocks_, and will trigger the creation of potentially complex HTML
  components;
- Control (and block) properties are read, and all referenced application variables are
  bound.
- Potentially, _callbacks_ are located and connected from the rendered page back to the Python code,
  if you want to watch user events (the notion of callbacks is detailed in the section [Callbacks](user_callbacks.md)).

### Registering the page

Once you have created an instance of a page renderer for a specified piece of
text, you can register that page to the [`Gui`](../reference/#taipy.gui.gui.Gui) instance
used by your application.

### Viewing the page

When the user browser connects to the Web server, requesting the indicated page,
the rendering takes place (involving the retrieval of the application variable
values) so you can see your application's state, and interact with it.

### Markdown processing

One of the page description format is the [Markdown](https://en.wikipedia.org/wiki/Markdown)
markup language.

Taipy uses [Python Markdown](https://python-markdown.github.io/) to translate Markdown
text to elements that are used to create Web pages. It also uses many extensions that
make it easier to create nice-looking page that user can enjoy. Specifically,
Taipy uses the following [Markdown extensions](https://python-markdown.github.io/extensions/):
[_Admonition_](https://python-markdown.github.io/extensions/admonition/),
[_Attribute Lists_](https://python-markdown.github.io/extensions/attr_list/),
[_Fenced Code Blocks_](https://python-markdown.github.io/extensions/fenced_code_blocks/),
[_Meta-Data_](https://python-markdown.github.io/extensions/meta_data/),
[_Markdown in HTML_](https://python-markdown.github.io/extensions/md_in_html/),
[_Sane Lists_](https://python-markdown.github.io/extensions/sane_lists/)
and [_Tables_](https://python-markdown.github.io/extensions/tables/).
Please refer to the Python Markdown package documentation to get information on how these are used.

Beside these extensions, Taipy adds its own, that can parse a Taipy-specific
construct that allows for defining controls (and all the properties they need)
and structuring elements.

The basic syntax for creating Taipy constructs in Markdown is: `<|...|...|>` (opening with a
_less than_ character immediately followed by a vertical bar character &#151; sometimes called
_pipe_ &#151; followed a potentially empty series of vertical bar-separated items, and closing
by a vertical bar character immediately followed by the _greater than_ character).<br/>Taipy
will interpret any text between the `<|` and the `|>` markers and try to make sense of it.

The most common use of this construct is to create controls. Taipy expects the control type
name to appear between the two first vertical bar character (like in `<|control|...}>`.

!!! important
    If the first fragment text is not the name of a control type, Taipy will consider this
    fragment to be the default value for the default property of the control, whose type name
    must then appear as the second element.

Every following elements will be interpreted as a property name-property value pair
using the syntax: _property\_name=property\_value_ (note that all space characters
are significative).  

!!! note "Shortcut for Boolean properties"
    Should the `=property_value` fragment be missing, the property value is interpreted as the
    Boolean value `True`.<br/>
    Furthermore if the property name is preceded by the text "_no&blank;_", "_not&blank;_",
    "_don't&blank;_" or "_dont&blank;_" (including the trailing space character) then no
    property value is expected, and the property value is set to `False`.

#### Some examples

!!! example "Multiple properties"
    You can have several properties defined in the same control fragment:
    ```
    <|button|label=Do something|active=False|>
    ```

!!! example "The _default property_ rule"
    The default property name for the control type [`button`](controls/button.md) is _label_. In Taipy,
    the Markdown text
    ```
    <|button|label=Some text|>
    ```
    Is exactly equivalent to
    ```
    <|Some text|button|>
    ```
    which is slightly shorter.

!!! example "The _missing Boolean property value_ rules"
    ```
    <|button|active=True|>
    ```
    is equivalent to
    ```
    <|button|active|>
    ```
    And
    ```
    <|button|active=False|>
    ```
    is equivalent to
    ```
    <|button|not active|>
    ```

There are a very few exceptions to the `<|control_type|...|>` syntax, that are described
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

!!! abstract "TODO: local resources documentation"
