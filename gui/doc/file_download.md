A control that allows to download a file.

The download can be triggered when clicking on a button, or can be performed automatically.

## Usage

### default behavior

Allows to download _content_ when content is a file path or some content

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download>{content}</taipy:file_download>
        ```

### standard configuration

A specific _label_ can be shown besides the standard icon. 
The function name provided as _on_action_ is called when the user initiate the download.
The _name_ provided will be the default name proposed to the user when downloading (depending on browser validation and rules).

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|label=Download File|on_action=function_name|name=filename|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download on_action="function_name"  name="filename">{content}</taipy:file_download>
        ```

### file preview in the browser

File content can be visualized in the browser (if supported and in another tab) by specifying _bypass_preview_ as False.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|bypass_preview=False|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download bypass_preview="False">{content}</taipy:file_download>
        ```

### automatic download

File content can be downloaded automatically (when the page shows or when the content is set).

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|auto|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download auto="True">{content}</taipy:file_download>
        ```