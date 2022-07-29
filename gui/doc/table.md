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
     The given function expects three parameters:
     - _state_: the current state
     - _index_: the index of the row in this table
     - _row_ (optional): all the values for this row
   - `style[_column_name_]`: this applies to a specific cell.
     The given function expects four parameters:
     - _state_: the current state
     - _value_: the value of the cell
     - _index_ (optional): the index of the row of this cell
     - _column_name_ (optional): the name of the column for this cell

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

