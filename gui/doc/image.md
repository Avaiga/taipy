A control that can display an image.

!!! Note "Image format"
    Note that if the content is provided as a buffer of bytes, it can be converted
    to an image content if and only if you have installed the
    [`python-magic`](https://pypi.org/project/python-magic/) Python package (as well
    as [`python-magic-bin`](https://pypi.org/project/python-magic-bin/) if your
    platform is Windows).

You can indicate a function to be called when the user clicks on the image.

## Styling

All the image controls are generated with the "taipy-image" CSS class. You can use this class
name to select the image controls on your page and apply style.

The [Stylekit](../styling/stylekit.md) also provides a specific CSS class that you can use to style
images:

- *inline*<br/>
  Displays an image as inline and vertically centered. It would otherwise be displayed as a block.
  This can be relevant when dealing with SVG images.

## Usage

### Default behavior

Shows an image specified as a local file path or as raw content.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|image|>
        ```
  
    === "HTML"

        ```html
        <taipy:image>{content}</taipy:image>
        ```

### Call a function on click

A specific _label_ can be shown over the image. 
The function name provided as _on_action_ is called when the image is clicked (same as button).

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|image|label=this is an image|on_action=function_name|>
        ```
  
    === "HTML"

        ```html
        <taipy:image on_action="function_name" label="This is an image">{content}</taipy:image>
        ```
