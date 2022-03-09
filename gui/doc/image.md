A control that can display an image.

You can indicate a function to be called when the user clicks on the image.

## Usage

### default behavior

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

### standard configuration

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
