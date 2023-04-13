A kind of [`input`](input.md) that handles numbers.


## Styling

All the number controls are generated with the "taipy-number" CSS class. You can use this class
name to select the number controls on your page and apply style.

### [Stylekit](../styling/stylekit.md) support

The [Stylekit](../styling/stylekit.md) provides a specific class that you can use to style number controls:

* *fullwidth*<br/>
    If a number control uses the *fullwidth* class, then it uses the whole available
    horizontal space.

## Usage

### Simple

You can create a <i>number</i> field bound to a numerical variable with the following content:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|number|>
        ```
  
    === "HTML"

        ```html
        <taipy:number>{value}</taipy:number>
        ```
