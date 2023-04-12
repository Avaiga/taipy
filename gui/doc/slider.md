Displays and allows the user to set a value within a range.

The range is set by the values `min` and `max` which must be integer values.

If the _lov_ property is used, then the slider can be used to select a value among the different choices.


## Styling

All the slider controls are generated with the "taipy-slider" CSS class. You can use this class
name to select the sliders on your page and apply style.

## Usage

### Selecting a value between 0 and 100

A numeric value can easily be represented and interacted with using the
following content:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|slider|>
        ```
  
    === "HTML"

        ```html
        <taipy:slider>{value}</taipy:slider>
        ```

### Constraining values

You can specify what bounds the value should be restrained to:

!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|slider|min=1|max=10|>
        ```
  
    === "HTML"

        ```html
        <taipy:slider min="1" max="10">{value}</taipy:slider>
        ```

### Changing orientation


!!! example "Page content"

    === "Markdown"

        ```
        <|{value}|slider|orientation=vert|>
        ```
  
    === "HTML"

        ```html
        <taipy:slider orientation="vertical">{value}</taipy:slider>
        ```
