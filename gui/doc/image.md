A control that can display an image.

You can indicate a function to be called when the user clicks on the image.

## Usage

### Default behavior

Shows an image specified as a local file path or as raw content.
The raw content is generated as a data base64 url 
if the size of the buffer is lesser than the limit set in the config (data_url_max_size with default value = 50kB).
The raw content is written to a temporary file if it's size is greater than the limit.

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
