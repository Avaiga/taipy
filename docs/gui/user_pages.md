# Pages

Pages are the base for your user interface. Pages hold text, images and controls that
display information that the application needs to publish, and ways to interact with
the application data.

Taipy lets you create as many pages as you want, with whatever content you need.
Pages are created using _page renderers_, that convert some text (inside the application
code or from an external file) into HTML content that is sent and rendered onto the client
device. The [Page renderers](#page-renderers) section provides the details you need to create
and expose your pages.

There are page fragments that you may want to repeat on different pages. In that situation
you will want to use the  [Partials](#partials) concept described below. This will avoid
repeating yourself when creating your user interfaces.

Application sometimes need to prompt the user to indicate a situation or request an
input of some sort. This need is covered in Taipy using the [`dialog`](controls/dialog.md)
control that is demonstrated in the [Dialogs](#dialogs) section below.

Modern user interface also provide small pages that pop out and be removed, for
temporary use such as providing specific parameters for the application. Taipy lets
you create such elements as described in the [Panes](#panes) section.

## Page renderers

A _page rendered_ is a Python class that reads some text (directly from a string, or
reading a text file) and converts it into a page that can be displayed in a browser.

There are different types of page renderers in Taipy but all follow the same core
principles: they parse some input text, locate the Taipy-specific constructs that
involve, in the case of Taipy controls, the creation of potentially complex HTML
components, bind these controls to application variables and connect _callbacks_
from the rendered page back to the Python code, if you want to watch user events
(the notion of callbacks is detailed in the section [Callbacks](user_callbacks.md)).

Once you have created an instance of a page renderer for a specified piece of
text, you can register that page to the [`Gui`](../reference/#taipy.gui.gui.Gui) instance
used by your application.  
When the user browser connects to the Web server, requesting the indicated page,
the rendering takes place (involving the retrieval of the application variable
values) and you can see your application's state, and interact with it.

### Markdown specifics

Taipy uses [Python Markdown](https://python-markdown.github.io/) to translate Markdown
text to elements that are used to create Web pages. It also uses many extensions that
make it easier to create nice-looking page that user can enjoy. Specifically,
Taipy uses the following extensions: _admonition_, _attr_list_, _fenced_code_, _meta_,_md_in_html_, _sane_lists_ and _tables_. Please refer to the Python Markdown package
documentation to get information on how these are used.  
Beside these extension, Taipy adds its own, that can parse a Taipy-specific
construct that allows for defining controls (and all the properties they need)
and structuring elements.

The basic syntax for creating Taipy constructs in Markdown is: _<|...|...|>_.  
Taipy will interpret any text between the _<|_ and the _|>_ markers and
try to make sense of it.

The most common use is to create controls. Taipy expects the control type name
to appear as the first _|...|_ element. If it fails to do so, Taipy will consider
the first element to be the default value for the default property of the control,
whose name must then appear as the second element.  
Every following elements will be interpreted as a property name-property value pair
using the syntax: _property_name_=_property_value_ (note that all space characters
are significative).  
Should the _=property_value_ fragment be missing, the property value is interpreted
as the Boolean value `True`.  
If the property name is preceded by the text "_no _", "_not _", "_don't _" or "_dont _"
(including the trailing space character) then no property value is expected, and the
property value is set to `False`.

!!! example "Some examples"
- Multiple properties:  
  You can have several properties defined in the same control fragment:  
  "_<|button|label=Do something|active=True|>_"
- The _default property_  rule:  
  The control type [`button`](controls/button.md) has a default property called _label_.  
  In Taipy, the Markdown text "_<|button|label=Some text|>_" is exactly equivalent
  to "_<|Some text|button|>_".
- The _missing Boolean property value_ rules:  
  "_<|button|active=True|>_" is equivalent to "_<|button|active|>_".  
  "_<|button|active=False|>_" is equivalent to "_<|button|not active|>_".

There are a very few exceptions to the _<|control_type|>_ syntax, that are described
in their respective documentation section. The most obvious exception being the
[`field`](controls/field.md) control, that can be created without even mentioning it's
type.

### HTML specifics

## The root page

## Partials

## Dialogs

## Panes

## Local resources
