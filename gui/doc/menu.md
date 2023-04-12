Shows a left-side menu.

This control is represented by a unique left-anchor and foldable vertical menu.

## Styling

All the menu controls are generated with the "taipy-menu" CSS class. You can use this class
name to select the menu controls on your page and apply style.

## Usage

### Defining a simple static menu

!!! example "Page content"

    === "Markdown"

        ```
        <|menu|lov=menu 1;menu 2|>
        ```
  
    === "HTML"

        ```html
        <taipy:menu lov="menu 1;menu 2"></taipy:menu>
        ```

### Calling a user-defined function

To have the selection of a menu item call a user-defined function, you must set the on_action
property to a function that you define:

You page can define a menu control like:

!!! example "Page content"

    === "Markdown"

        ```
        <|menu|lov=menu 1;menu 2|on_action=my_menu_action>
        ```
  
    === "HTML"

        ```html
        <taipy:menu lov="menu 1;menu 2" on_action="my_menu_action"></taipy:menu>
        ```

Your Python script must define the my_menu_action function:

```def my_menu_action(state, ...):
  ...
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


