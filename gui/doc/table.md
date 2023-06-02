Displays a data set as tabular data.

## Details

### Data types

All the data sets represented in the table control must be assigned to
its [*data*](#p-data) property.

The supported types for the [*data*](#p-data) property are:

- A list of values:<br/>
    When receiving a *data* that is just a series of values, the table is made of a single column holding
    the values at the corresponding index. The column name is then "0".
- A [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html):<br/>
    Taipy tables then use the same column names as the DataFrame's.
- A dictionary:<br/>
    The value is converted into a Pandas DataFrame where each key/value pair is converted
    to a column named *key* and the associated value. Note that this will work only when
    all the values of the dictionary keys are series that have the same length.
- A list of lists of values:<br/>
    All the lists must be the same length. The table control creates one row for each list in the
    collection.
- A Numpy series:<br/>
    Taipy internally builds a Pandas DataFrame with the provided *data*.
 
### Display modes

The table component supports three display modes:

- *paginated*: you can choose the page size and page size options. The [*allow_all_rows*](#p-allow_all_rows)
  property makes it possible to add an option to show a page with all rows.
- *unpaginated*: all rows and no page are shown. That is the setting when the [*show_all*](#p-show_all)
  property is set to True.
- *auto_loading*: the pages are loaded on demand depending on the visible area. That is the behavior when
  the [*auto_loading*](#p-auto_loading) property is set to True.

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

### Dynamic styling

You can modify the style of entire rows or specific table cells based on any criteria, including
the table data itself.

When Taipy creates the rows and the cells, it can add a specific CSS class to the generated elements.
This class name is the string returned by the function set to the [*style*](#p-style) property for entire rows,
or [*style[column_name]*](#p-style[column_name]) for specific cells.

The signature of this function depends on which *style* property you use:

   - [*style*](#p-style): this applies to entire rows.<br/>
     The given function expects three optional parameters:
     - *state*: the current state
     - *index*: the index of the row in this table
     - *row*: all the values for this row
   - [*style[column_name]*](#p-style[column_name]): this applies to a specific cell.<br/>
     The given function expects five optional parameters:
     - *state*: the current state
     - *value*: the value of the cell
     - *index*: the index of the row in this table
     - *row*: all the values for this row
     - *column_name*: the name of the column for this cell

Based on these parameters, the function must return a string that defines a CSS class name that will
be added to the CSS classes for this table row or this specific cell.<br/>
The [example](#styling-rows) below shows how this works.

## Usage

### Show tabular data

Suppose you want to display the data set defined as follows:

```py
# x_range = [-10, -6, -2, 2, 6, 10]
x_range = range(-10, 11, 4)

data = {
    "x": x_range,
    # y1 = x*x
    "y1": [x*x for x in x_range],
    # y2 = 100-x*x
    "y2": [100-x*x for x in x_range]
}
```

You can use the following control declaration to display all these numbers
in a table:

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|>
        ```
    === "HTML"
        ```html
        <taipy:table data="{data}" />
        ```

The resulting image looks like this:
<figure class="tp-center">
    <img src="../table-simple-d.png" class="visible-dark"  width="50%"/>
    <img src="../table-simple-l.png" class="visible-light" width="50%"/>
    <figcaption>A simple table</figcaption>
</figure>

### Large data

The example above had only six lines of data. If we change the *x_range* definition
to create far more data lines, we come up with a table with much more data to display:
```py
# x_range = [-10, -9.98, ..., 9.98, 10.0] - 1000 x values
x_range = [round(20*i/1000-10, 2) for i in range(0, 1001)]

data = {
    "x": large_x_range,
    # y1 = x*x
    "y1": [round(x*x, 5) for x in large_x_range],
    # y2 = 100-x*x
    "y2": [round(100-x*x, 5) for x in large_x_range]
}
```

We can use the same table control definition:

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|>
        ```
    === "HTML"
        ```html
        <taipy:table data="{data}" />
        ```

To get a rendering looking like this:
<figure class="tp-center">
    <img src="../table-page-d.png" class="visible-dark"  width="50%"/>
    <img src="../table-page-l.png" class="visible-light" width="50%"/>
    <figcaption>Paginated table (partial)</figcaption>
</figure>

Only the first 100 rows (as indicated in the 'Rows per page' selector) are visible.<br/>
The table scroll bar lets you navigate across the 100 first rows.<br/>
You can change how many rows are displayed simultaneously using the
[*page_size*](#p-page_size) and [*page_size_options*](#p-page_size_options) properties.

If you want to display all the rows at the same time, you can change the control definition
to add the [*show_all](#p-show_all):

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|show_all|>
        ```
    === "HTML"
        ```html
        <taipy:table data="{data}" show_all="true"/>
        ```

Now the table displays all the data rows, and the scrollbar lets you navigate among all of
them:

<figure class="tp-center">
    <img src="../table-show_all-d.png" class="visible-dark"  width="50%"/>
    <img src="../table-show_all-l.png" class="visible-light" width="50%"/>
    <figcaption>Showing all the rows (partial)</figcaption>
</figure>

Setting the [*allow_all_rows*](#p-allow_all_rows) property to True for a paginated table
adds the 'All' option to the page size options, so the user can switch from one mode to
the other.

### Show specific columns

If you want to display a specific set of columns, you can use the [*columns*](#p-columns)
property to indicate what columns should be displayed.

Here is how you would define the table control if you want to hide the column *y2*
from the examples above:

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|columns=x;y1|>
        ```

    === "HTML"
        ```html
        <taipy:table columns="x;y1">{data}</taipy:table>
        ```

And the *y2* column is not displayed any longer:
<figure class="tp-center">
    <img src="../table-columns-d.png" class="visible-dark"  width="50%"/>
    <img src="../table-columns-l.png" class="visible-light" width="50%"/>
    <figcaption>Specifying the visible columns</figcaption>
</figure>

### Styling rows

To give a specific style to a table row, you will use the [*style*](#p-style) property.<br/>
This property holds a function that is invoked when each row is rendered, and it must return
the name of a style, defined in CSS.

Here is how a row styling function can be defined:

```py
def even_odd_style(_1, index, _2):
    if index % 2:
        return "blue-cell"
    else:
        return "red-cell"
```

We only use the second parameter since, in this straightforward case, we do not need the application
*state* (first parameter) or the values in the row (third parameter).<br/>
Based on the row index (received in *index*), this function returns the name of the style to apply
to the row: "blue-cell" if the index is odd, "red-cell" if it is even.

We need to define what these style names mean. This is done in a CSS stylesheet, where the following
CSS content would appear:

```css
.blue-cell>td {
    color: white;
    background-color: blue;
}
.red-cell>td {
    color: yellow;
    background-color: red;
}
```

Note that the style selectors use the CSS child combinator selector "&gt;" to target elements
that hold a `td` element (the cells themselves).

To use this style, we can adjust the control definition used above so it looks like this:

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|style=even_odd_style|>
        ```

    === "HTML"
        ```html
        <taipy:table data="{data}" style="even_odd_style" />
        ```

The resulting display will be what we expected:

<figure class="tp-center">
    <img src="../table-rowstyle-d.png" class="visible-dark"  width="50%"/>
    <img src="../table-rowstyle-l.png" class="visible-light" width="50%"/>
    <figcaption>Styling the rows</figcaption>
</figure>

Note that the styling function is so simple that we could have made it a lambda, directly
in the control definition:

!!! example "Alternative page content"
    === "Markdown"
        ```
        <|{data}|table|style={lambda s, idx, r: "blue-cell" if idx % 2 == 0 else "red-cell"}|>
        ```

    === "HTML"
        ```html
        <taipy:table data="{data}" style="{lambda s, idx, r: "blue-cell" if idx % 2 == 0 else "red-cell"}" />
        ```


### Aggregation

To get the aggregation functionality in your table, you must indicate which columns can be aggregated
and how to perform the aggregation.

This is done using the indexed [*group_by*](#p-group_by[column_name]) and
[*apply*](#p-apply[column_name]) properties.

The [*group_by[column_name]*](#p-group_by[column_name]) property, when set to True indicates that the
column *column_name* can be aggregated.

The function provided in the [*apply[column_name]*](#p-apply[column_name]) property indicates how to
perform this aggregation. The value of this property, which is a string, can be:

- A built-in function. Available predefined functions are the following: `count`, `sum`, `mean`, `median`,
  `min`, `max`, `std`, `first` (the default value), and `last`.
- The name of a user-defined function or a lambda function.<br/>
  This function receives a single parameter which is the series to aggregate, and it must return a scalar
  value that would result from the aggregation.

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|group_by[Group column]|apply[Apply column]=count|>
        ```

    === "HTML"
        ```html
        <taipy:table data="{data}" group_by[Group column]="True" apply[Apply column]="count" />
        ```

### Cell tooltips

You can specify a tooltip for specific table cells.

When Taipy creates the cells, it can add a specific tooltip that you would have set as the
return value of the function set to the [*tooltip*](#p-tooltip) or
[*tooltip[column_name]*](#p-tooltip[column_name]) properties.

The signature of this function expects five optional parameters:
- *state*: the current state.
- *value*: the value of the cell.
- *index*: the index of the row in this table.
- *row*: all the values for this row.
- *column_name*: the name of the column for this cell.

Based on these parameters, the function must return a string that defines a tooltip used as the
cell's tooltip text.

!!! example "Page content"
    === "Markdown"
        ```
        <|{data}|table|tooltip={lambda state, val, idx: "A tooltip" if idx % 2 == 0 else "Another tooltip"}|>
        ```

    === "HTML"
        ```html
        <taipy:table data="{data}" tooltip="{lambda state, idx, col: 'A tooltip' if idx % 2 == 0 else 'Another tooltip'}" />
        ```
