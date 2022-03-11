Shows a left side menu.

This control is represented by a unique left-anchor and foldable vertical menu.

## Usage

### Defining a simple static menu

The property _on_action_ default value is "on_menu_action"; a function with that name will be called if present.
The parameter payload["args"] holds a list that contains the id of the selected menu.

!!! example "Page content"

    === "Markdown"

        ```
        <|menu|lov=menu 1;menu 2|>
        ```
  
    === "HTML"

        ```html
        <taipy:menu lov="menu 1;menu 2"></taipy:menu>
        ```

### Disabling menu options

The property _inactive_ids_ can be set to dynamically disable any specific menu options.

!!! example "Page content"

    === "Markdown"

        ```
        <|menu|lov=menu 1;menu 2;menu 3|inactive_ids=menu 2;menu 3|>
        ```
  
    === "HTML"

        ```html
        <taipy:menu lov="menu 1;menu 2" inactive_ids="menu 2;menu 3"></taipy:menu>
        ```

### Adjusting presentation

The property _label_ defines the text associated with the main Icon.
The properties _width_ and _width[mobile]_ specify the requested width of the menu when expanded.

!!! example "Page content"

    === "Markdown"

        ```
        <|menu|lov=menu 1;menu 2;menu 3|label=Menu title|width=15vw|width[mobile]=80vw|>
        ```
  
    === "HTML"

        ```html
        <taipy:menu lov="menu 1;menu 2" label="Menu title" width="15vw" width[mobile]="80vw"></taipy:menu>
        ```

### Menu icons

As for every control that deals with lov, each menu option can display an image (see Icon^) and/or some text.

!!! example "Page content"

    === "Markdown"

        ```
        <|menu|lov={[("id1", Icon("/images/icon.png", "Menu option 1")), ("id2", "Menu option 2")]}|>
        ```
  
    === "HTML"

        ```html
        <taipy:menu>{[("id1", Icon("/images/icon.png", "Menu option 1")), ("id2", "Menu option 2")]}</taipy:menu>
        ```


