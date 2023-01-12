Displays data sets in a chart or a group of charts.

The chart control is based on the [plotly.js](https://plotly.com/javascript/)
graphs library.

Plotly is a graphing library that provides a vast number of visual
representations of datasets with all sorts of customization capabilities. Taipy
exposes the Plotly components through the `chart` control and heavily depends on
the underlying implementation.

The core principles of how to create charts in Taipy are explained in the
[Basic concepts](charts/basics.md) section.

# Description

A chart control can hold several traces, that can display individual data sets.<br/>
To indicate properties for a given trace, you will use the indexed properties
(using the *property_name[index]* syntax, with the indices starting at index 1) to
specify which trace you target.

Indexed properties can have a default value (using the *property_name* syntax with
no index) which is overridden by any specified indexed property:<br/>
if `indexed_property` is an indexed property, you can set it to a value, that is
then applied to all the traces. If you later reference that property with an index, the
value will apply only for the indicated trace.
```
general_value = <some_value>
specific_value = <some_other_value>

page = "<|...|chart|...|index_property={general_value}|index_property[2]={specific_value}|...|>"
```
creates a chart where *general_value* is used for all the traces, except for the one with index 2.

An indexed property can also be assigned an array. Then each array value is set to the appropriate
index, in sequence:
```
values = [
    value1,
    value2,
    value3
]
    
page = "<|...|chart|...|index_property={values}|...|>"
```
is equivalent to
```
page = "<|...|chart|...|index_property[1]={value1}|index_property[2]={value2}|index_property[3]={value3}|...|>"
```

or even shorter:
```
page = "<|...|chart|...|index_property={value1}|index_property[2]={value2}|index_property[3]={value3}|...|>"
```

Supported types for the *data* property types are:

- A Pandas DataFrame;
- A Dictionary: converted into a Pandas DataFrame where each key/value pair is converted
  to a column named *key* and the associated value;
- A list of lists;
- A Numpy series;
- A list of Pandas DataFrames;
- A list of dictionaries, which is converted to a list of Pandas DataFrames.


## Usage

Here is a list of several sub-sections that you can check to get more details on a specific
areas covered by the chart control:

- [Basic concepts](charts/basics.md)
