Displays a data set as tabular data.

The table component supports 3 display modes:

   - _paginated_: you can choose the page size and page size options (`allow_all_rows` adds an option to show a page with all rows).
   - _unpaginated_:  all rows and no page are shown (`show_all = True`).
   - _auto_loading_: the pages are loaded on demand depending on the visible area.

The _data_ property supported types are:

- pandas Dataframe
- array of arrays
- numpy series

Data columns are accessed by their name or index (temporary dataframes are built from these different sources).


## Styling

All the table controls are generated with the "taipy-table" CSS class. You can use this class
name to select the tables on your page and apply style.

### [Stylekit](../styling/stylekit.md) support

The [Stylekit](../styling/stylekit.md) provides a CSS custom property:

- *--table-stripe-opacity*<br/>
  This property contains the opacity applied to odd lines of tables.<br/>
  The default value is 0.5.

The [Stylekit](../styling/stylekit.md) also provides specific CSS classes that you can use to style
tables:

- *header-plain*<br/>
  Adds a plain and contrasting background color to the table header.
- *rows-bordered*<br/>
  Adds a bottom border to each row.
- *rows-similar*<br/>
  Removes the even-odd striped background so all rows have the same background.

## Usage

### Show a table

If you want to create a table that represents a dataframe stored in the Python
variable _data_ (all columns will be displayed), you can use the following content:

!!! example "Page content"

    === "Markdown"

        ```
        <|{data}|table|>
        ```

    === "HTML"

        ```html
        <taipy:table data="{data}" />
        ```

### Show specific columns

!!! example "Page content"

    === "Markdown"

        ```
        <|{data}|table|columns=Col 1;Col 2;Col 3|page_size=10|page_size_options=10;30;100|date_format=eee dd MMM yyyy|not allow_all_rows|show_all=No|auto_loading=False|width=100vw|height=100vw|selected={selection}|>
        ```

    === "HTML"

        ```html
        <taipy:table columns="Col 1;Col 2;Col 3" page_size="10" page_size_options="10;30;100" date_format="eee dd MMM yyyy" allow_all_rows="False" show_all="False" auto_loading="False" width="100vw" height="100vw" selected="{selection}">{data}</taipy:table>
        ```

### Aggregation

To get the aggregation functionality in your table, you must indicate which columns can be aggregated, and
how to perform the aggregation.

This is done using the _group_by_ and _apply_ properties.

The _group_by[column_name]_ property, when set to _True_ indicates that the column _column_name_ can be
aggregated.

The function provided in the _apply[column_name]_ property indicates how to perform this aggregation.
The value of this property, which is a string, can be:

   - A built-in function. Available predefined functions are the following: `count`, `sum`, `mean`, `median`,
     `min`, `max`, `std`, `first` (the default value), and `last`.
   - The name of a user-defined function, or a lambda function.<br/>
     This function receives a single parameter which is the series to aggregate, and it must return a scalar value which would
     be the result of the aggregation.

!!! example "Page content"

    === "Markdown"

        ```
        <|{data}|table|group_by[Group column]|apply[Apply column]=count|>
        ```

    === "HTML"

        ```html
        <taipy:table data="{data}" group_by[Group column]="True" apply[Apply column]="count" />
        ```

### Styling

You can modify the style of entire rows or specific table cells.

When Taipy creates the rows and the cells, it can add a specific CSS class that you would have set as the
return value of the function set to the `style` property, for entire rows, or `style[_column_name_]`, for
specific cells.

The signature of this function depends on which `style` property you use:

   - `style`: this applies to entire rows.
     The given function expects three optional parameters:
     - _state_: the current state
     - _index_: the index of the row in this table
     - _row_: all the values for this row
   - `style[_column_name_]`: this applies to a specific cell.
     The given function expects five optional parameters:
     - _state_: the current state
     - _value_: the value of the cell
     - _index_: the index of the row in this table
     - _row_: all the values for this row
     - _column_name_: the name of the column for this cell

Based on these parameters, the function must return a string that defines a CSS class name that will
be added to the CSS classes for this table row or this specific cell.

You can then add the definition of this class in your CSS file.

!!! example "Page content"

    === "Markdown"

        ```
        <|{data}|table|style={lambda state, idx, row: "red-row" if idx % 2 == 0 else "blue-row"}|>
        ```

    === "HTML"

        ```html
        <taipy:table data="{data}" style="{lambda state, idx, row: 'red-row' if idx % 2 == 0 else 'blue-row'}" />
        ```

Css definition
```css
.red-row td {
  background-color: red;
}
.blue-row td {
  background-color: blue;
}
```

### Cell Tooltip

You can specify a tooltip for specific table cells.

When Taipy creates the cells, it can add a specific tooltip that you would have set as the
return value of the function set to the _tooltip_ or _tooltip[column_name]_ property .

The signature of this function expects five optional parameters:
     - _state_: the current state
     - _value_: the value of the cell
     - _index_: the index of the row in this table
     - _row_: all the values for this row
     - _column_name_: the name of the column for this cell

Based on these parameters, the function must return a string that defines a tooltip that is
used as the cell's tooltip text.

!!! example "Page content"

    === "Markdown"

        ```
        <|{data}|table|tooltip={lambda state, val, idx: "some tooltip" if idx % 2 == 0 else "some other tooltip"}|>
        ```

    === "HTML"

        ```html
        <taipy:table data="{data}" tooltip="{lambda state, idx, col: 'some tooltip' if idx % 2 == 0 else 'some other tooltip'}" />
        ```
