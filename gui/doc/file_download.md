Allows downloading of a file content.


!!! Note "Image format"
    Note that if the content is provided as a buffer of bytes, it can be converted
    to an image content if and only if you have installed the
    [`python-magic`](https://pypi.org/project/python-magic/) Python package (as well
    as [`python-magic-bin`](https://pypi.org/project/python-magic-bin/) if your
    platform is Windows).
    
The download can be triggered when clicking on a button, or can be performed automatically.

## Styling

All the file download controls are generated with the "taipy-file_download" CSS class. You can use this class
name to select the file download controls on your page and apply style.

## Usage

### Default behavior

Allows downloading _content_ when content is a file path or some content.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download>{content}</taipy:file_download>
        ```

### Standard configuration

A specific _label_ can be shown beside the standard icon.

The function name provided as _on_action_ is called when the user initiates the download.

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

### Preview file in the browser

The file content can be visualized in the browser (if supported and in another tab) by setting _bypass_preview_ to False.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|bypass_preview=False|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download bypass_preview="False">{content}</taipy:file_download>
        ```

### Automatic download

The file content can be downloaded automatically (when the page shows and when the content is set).

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_download|auto|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_download auto="True">{content}</taipy:file_download>
        ```
