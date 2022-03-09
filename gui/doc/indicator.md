Displays a label on a red to green scale at a specific position.

The _min_ value can be greater than the _max_ value.<br/>
The value will be maintained between min and max.

## Usage

### default behavior

Shows a message at a specified position between min and max.

!!! example "Page content"

    === "Markdown"

        ```
        <|message|indicator|value={val}|min=0|max=100|>
        ```
  
    === "HTML"

        ```html
        <taipy:indicator value="{val}" min="0" max ="100">message</taipy:indicator>
        ```

### formatting the message

A _format_ can be applied to the message. 

!!! example "Page content"

    === "Markdown"

        ```
        <|{50}|indicator|format=%.2f|value=10|>
        ```
  
    === "HTML"

        ```html
        <taipy:indicator format="%.2f" value="10">{50}</taipy:indicator>
        ```


### vertical orientation

The _orientation_ of the indicator can be specified as vertical. 

!!! example "Page content"

    === "Markdown"

        ```
        <|{50}|indicator|orientation=v|value=10|>
        ```
  
    === "HTML"

        ```html
        <taipy:indicator orientation="vertical" value="10">{50}</taipy:indicator>
        ```
