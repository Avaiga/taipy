Allows uploading a file content.

The upload can be triggered by pressing a button, or drag-and-dropping a file on top of the control.

## Styling

All the file selector controls are generated with the "taipy-file_selector" CSS class. You can use this class
name to select the file selector controls on your page and apply style.

## Usage

### Default behavior

The variable specified in _content_ is populated by a local filename when the transfer is completed.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_selector|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_selector>{content}</taipy:file_selector>
        ```

### Standard configuration

A specific _label_ can be shown besides the standard icon. 
The function name provided as _on_action_ is called when the transfer is completed.
The _extensions_ property can be used as a list of file name extensions that is used to filter the file selection box. This filter is not enforced: the user can select and upload any file.
Upon dragging a file over the button, the _drop_message_ content is displayed as a temporary label for the button.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_selector|label=Download File|on_action=function_name|extensions=.csv,.xlsx|drop_message=Drop Message|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_selector on_action="function_name" extensions=".csv,.xlsx" drop_message="Drop Message">{content}</taipy:file_selector>
        ```

### Multiple files upload

The user can transfer multiple files at once by setting the _multiple_ property to True.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_selector|multiple|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_selector multiple="True">{content}</taipy:file_selector>
        ```
