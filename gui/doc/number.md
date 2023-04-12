A kind of [`input`](input.md) that handles numbers.


## Styling

All the number controls are generated with the "taipy-number" CSS class. You can use this class
name to select the number controls on your page and apply style.

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
