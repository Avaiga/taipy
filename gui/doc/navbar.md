A navigation bar control.

This control is implemented as a list of links.

## Styling

All the navbar controls are generated with the "taipy-navbar" CSS class. You can use this class
name to select the navbar controls on your page and apply style.

### [Stylekit](../styling/stylekit.md) support

The [Stylekit](../styling/stylekit.md) provides a specific class that you can use to style navbar controls:

* *fullheight*<br/>
  Ensures the tabs fill the full height of their container (in a header bar for example).

## Usage

### Defining a default navbar

The list of all pages registered in the Gui instance is used to build the navbar.

!!! example "Page content"

    === "Markdown"

        ```
        <|navbar|>
        ```
  
    === "HTML"

        ```html
        <taipy:navbar></taipy:navbar>
        ```


### Defining a custom navbar

The _lov_ property is used to define the list of elements that are displayed.
If a lov element id starts whith http, the page is opened in another tab.

!!! example "Page content"

    === "Markdown"

        ```
        <|navbar|lov={[("page1", "Page 1"), ("http://www.google.com", "Google")]}|>
        ```
  
    === "HTML"

        ```html
        <taipy:navbar lov={[("page1", "Page 1"), ("http://www.google.com", "Google")]}></taipy:navbar>
        ```
