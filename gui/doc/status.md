Displays a status or a list of statuses.

## Styling

All the status controls are generated with the "taipy-status" CSS class. You can use this class
name to select the status controls on your page and apply style.

## Usage

_value_ can be a list of tuples:

   - first element: *status*
   - second element: *message*

or a list of dictionaries that contain the keys:

       - *status*
       - *message*

### Show the current status

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|status|>
        ```
  
    === "HTML"

        ```html
        <taipy:status>{value}</taipy:status>
        ```

### Prevent status dismiss

If you don't want the user to be allowed to dismiss the displayed statuses, you can use the _without_close_ property.

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|status|without_close|>
        ```
  
    === "HTML"

        ```html
        <taipy:status without_close="True">{value}</taipy:status>
        ```
