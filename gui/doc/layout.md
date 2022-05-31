Organizes its children into cells in a regular grid.

The _columns_ property follows the [CSS standard](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-columns) syntax.
If the _columns_ property contains only digits and spaces, it is considered as flex-factor unit:
"1 1" => "1fr 1fr"

## Usage

### Default layout

The default layout contains 2 columns in desktop mode and 1 column in mobile mode.

!!! example "Page content"

    === "Markdown"

        ```
        <|layout|

            <|{some content}|>

        |>
        ```
  
    === "HTML"

        ```html
        <taipy:layout>

            <taipy:text>{some content}</taipy:text>

        </taipy:layout>
        ```


### Specifying gap

The _gap_ between adjacent cells is set by default to 0.5rem and can be specified.

!!! example "Page content"

    === "Markdown"

        ```
        <|layout|gap=20px|
            ...
            <|{some content}|>
            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:layout gap="20px">
            ...
            <taipy:text>{some content}</taipy:text>>
            ...
        </taipy:layout>
        ```

### Layout with a central "greedy" column

You can use the fr CSS unit so that the middle column use all the available space.

!!! example "Page content"

    === "Markdown"

        ```
        <|layout|columns=50px 1fr 50px|

            <|{1st column content}|>

            <|{2nd column content}|>

            <|{3rd column content}|>

            <|{1st column and second row content}|>

            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:layout columns="50px 1fr 50px">
            <taipy:part>
                <taipy:text>{1st column content}</taipy:text>
            </taipy:part>
            <div>
                <taipy:text>{2nd column content}</taipy:text>
            </div>
            <taipy:part>
                <taipy:text>{3rd column content}</taipy:text>
            </taipy:part>
            <taipy:part>
                <taipy:text>{1st column and second row content}</taipy:text>
            </taipy:part>
            ...
        </taipy:layout>
        ```

### Different layout for desktop and mobile devices

The _columns[mobile]_ property allows to specify a different layout when running on a mobile device.

!!! example "Page content"

    === "Markdown"

        ```
        <|layout|columns=50px 1fr 50px|columns[mobile]=1 1|

            <|{1st column content}|>

            <|{2nd column content}|>

            <|{3rd column content or 2nd row 1st column on mobile}|>

            <|{1st column and second row content or 2nd row 2nd column on mobile}|>

            ...
        |>
        ```
  
    === "HTML"

        ```html
        <taipy:layout columns="50px 1fr 50px" columns[mobile]="1 1">
            <taipy:part>
                <taipy:text>{1st column content}</taipy:text>
            </taipy:part>
            <div>
                <taipy:text>{2nd column content}</taipy:text>
            </div>
            <taipy:part>
                <taipy:text>{3rd column content or 2nd row 1st column on mobile}</taipy:text>
            </taipy:part>
            <taipy:part>
                <taipy:text>{1st column and second row content or 2nd row 2nd column on mobile}</taipy:text>
            </taipy:part>
            ...
        </taipy:layout>
        ```
