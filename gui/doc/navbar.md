A navigation bar control.

This control is implemented as a list of links.

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
If an lov element id starts whith http, the page is opened in another tab.

!!! example "Page content"

    === "Markdown"

        ```
        <|navbar|lov={[("page1", "Page 1"), ("http://www.google.com", "Google")]}|>
        ```
  
    === "HTML"

        ```html
        <taipy:navbar lov={[("page1", "Page 1"), ("http://www.google.com", "Google")]}></taipy:navbar>
        ```
