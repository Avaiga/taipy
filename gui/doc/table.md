Displays a data set as tabular data.

The table component supports 3 display modes:
   - _paginated_: you can choose the page size and page size options (`allow_all_rows` adds an option to show a page with all rows).
   - _unpaginated_:  all rows and no page are shown (`show_all = True`).
   - _auto_loading_: the pages are loaded on demand depending on the visible area.

## Details

### Properties

    - `selected`: TODO describe


### <a name="aggregation"></a>Aggregation

To get the aggregation functionality in your table, you must indicate which columns can be aggregated, and
how to perform the aggregation.<br/>
This is done using the _group_by_ and _apply_ properties.

The _group_by[column_name]_ property, when set to _True_ indicates that the column _column_name_ can be
aggregated.<br/>
The function provided in the _apply[column_name]_ property indicates how to perform this aggregation.
The value of this property, which is a string, can be:

   - A built-in function. Available predefined functions are the following: `count`, `sum`, `mean`, `median`,
     `min`, `max`, `std`, `first` (the default value) and `last`.
   - The name of a user-defined function, or a lambda function.<br/>
     This function receives a single parameter which is the series to aggregate, and it must return a scalar value which would
     be the result of the aggregation.

[TODO: Add short example ie. sum or sum/average]

### <a name="styling"></a>Styling

You can modify the style of entire rows or specific table cells.

When Taipy creates the rows and the cells, it can add a specific CSS class that you would have set as the
return value of the function set to the `style` property, for entire rows, or `style[_column_name_]`, for
specific cells.

The signature of this function depends on which `style` property you use:

   - `style`: this applies to entire rows.
     The given function expects two parameters:
     - _index_: the index of the row in this table
     - _ row_ (optional?): all the values for this row
   - `style[_column_name_]`: this applies to a specific cell.
     The given function expects four parameters:
     - _value_: the value of the cell
     - _index_ (optional?): the index of the row of this cell
     - _column_name_ (optional?): the name of the column for this cell

Based on these parameters, the function must return a string that defines a CSS class name that will
be added to the CSS classes for this table row, or this specific cell.

You can then add the definition of this class in your CSS file.

[TODO: Add short example ie. odd/even lines]

## Usage

### Simple

<code><|{value}|table|></code>

### Advanced

<code><|{value}|table|page_size=10|page_size_options=10;30;100|columns=Col 1;Col 2;Col 3|date_format=eee dd MMM yyyy|not allow_all_rows|show_all=No|auto_loading=False|width=100vw|height=100vw|selected={selection}|></code>

or with properties

<code><|{value}|table|properties={properties}|selected={selection}|></code>

