Displays data sets in a chart or a group of charts.

The chart control is based on the [plotly.js](https://plotly.com/javascript/)
graphs library.

Plotly is a graphing library that provides a vast number of visual
representations of datasets with all sorts of customization capabilities. Taipy
exposes the Plotly components through the `chart` control and heavily depends on
the underlying implementation.

The core principles of creating charts in Taipy are explained in the
[Basic concepts](charts/basics.md) section.<br/>
Advanced concepts are described in the [Advanced features](charts/advanced.md) section.

# Description

The chart control has a large set of properties to deal with the many types of charts
it supports and the different kinds of customization that can be defined.

### The *data* property

All the data sets represented in the chart control must be assigned to
its [*data*](#p-data) property.

The supported types for the [*data*](#p-data) property are:

- A list of values:<br/>
    Most chart types use two axes (*x*/*y* or *theta*/*r*). When receiving a *data* that is just
    a series of values, Taipy sets the first axis values to the value index ([0, 1, ...]) and
    the values of the second axis to the values of the collection.
- A [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html):<br/>
    Taipy charts can be defined by setting the appropriate axis property value to the DataFrame
    column name.
- A dictionary:<br/>
    The value is converted into a Pandas DataFrame where each key/value pair is converted
    to a column named *key* and the associated value. Note that this will work only when
    all the values of the dictionary keys are series that have the same length.
- A list of lists of values:<br/>
    If all the lists have the same length, Taipy creates a Pandas DataFrame with it.<br/>
    If sizes differ, then a DataFrame is created for each list, with a single column
    called "*&lt;index&gt;*/0" where *index* is the index of the current list in the *data*
    array. Then an array is built using all those DataFrames and used as described
    below.
- A Numpy series:<br/>
    Taipy internally builds a Pandas DataFrame with the provided *data*.
- A list of Pandas DataFrames:<br/>
    This can be used when your chart must represent data sets of different sizes. In this case,
    you must set the axis property ([*x*](#p-x), [*y*](#p-y), [*r*](#p-r), etc.) value to a string
    with the format: "*&lt;index&gt;*/*&lt;column&gt;*" where *index* is the index of the DataFrame
    you want to refer to (starting at index 0) and *column* would be the column name of the
    referenced DataFrame.
- A list of dictionaries<br/>
    The *data* is converted to a list of Pandas DataFrames.

### Indexed properties

Chart controls can hold several traces that may display different data sets.<br/>
To indicate properties for a given trace, you will use the indexed properties
(the ones whose type is *indexed(type)*). When setting the value of an indexed
property, you can specify which trace this property should apply to: you will
use the *property_name[index]* syntax, where the indices start at index 1, to
specify which trace is targeted for this property.

Indexed properties can have a default value (using the *property_name* syntax with
no index) which is overridden by any specified indexed property:<br/>
Here is an example where *i_property* is an indexed property:

```
# This value applies to all the traces of the chart control
general_value = <some_value>
# This value applies to only the second trace of the chart control
specific_value = <some_other_value>

page = "<|...|chart|...|i_property={general_value}|i_property[2]={specific_value}|...|>"
```

In the definition for *page*, you can see that the value *general_value* is set to the
property without the index operator ([]) syntax. That means it applies to all the traces
of the chart control.<br/>
*specific_value*, on the other hand, applies only to the second trace.

An indexed property can also be assigned an array, without the index operator syntax.
Then each value of the array is set to the property at the appropriate index, in sequence:

```
values = [
    value1,
    value2,
    value3
]
    
page = "<|...|chart|...|i_property={values}|...|>"
```

is equivalent to

```
page = "<|...|chart|...|i_property[1]={value1}|i_property[2]={value2}|i_property[3]={value3}|...|>"
```

or slightly shorter (and if there are no more than three traces):

```
page = "<|...|chart|...|i_property={value1}|i_property[2]={value2}|i_property[3]={value3}|...|>"
```

## Usage

Here is a list of several sub-sections that you can check to get more details on a specific
domain covered by the chart control:

- [Basic concepts](charts/basics.md)
