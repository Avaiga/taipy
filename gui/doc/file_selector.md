A control that allows to upload files.

The upload can be triggered by pressing a button, or drag-and-dropping a file on top of the control.

## Usage

### default behavior

The variable specified in _content_ is populated by a local filename when transfer is finished.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_selector|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_selector>{content}</taipy:file_selector>
        ```

### standard configuration

A specific _label_ can be shown besides the standard icon. 
The function name provided as _on_action_ is called when the transfer is finished.
The _extensions_ property is a list of extensions that is used to filter the file selction box but won't be enforced ie the suer can select and upload any file.
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

### multiple files upload

The user can transfer multiple files at once by specifying the _multiple_ property as True.

!!! example "Page content"

    === "Markdown"

        ```
        <|{content}|file_selector|multiple|>
        ```
  
    === "HTML"

        ```html
        <taipy:file_selector multiple="True">{content}</taipy:file_selector>
        ```
