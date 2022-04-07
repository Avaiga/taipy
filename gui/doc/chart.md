Displays data sets in a chart or a group of charts.

The chart control is based on the [plotly.js](https://plotly.com/javascript/)
graphs library.

A chart control can hold several traces, that can display individual data sets.  

To indicate properties for a given trace, you will use the indexed properties
(using the *property_name[index]* syntax, with the indices starting at index 1) to
specify which trace you target.

Indexed properties can have a default value (using the *property_name* syntax with
no index) which is overridden by any specified indexed property.

The _data_ property supported types are:
- pandas Dataframe
- list of lists
- numpy series
- list of pandas dataframes

## Usage

Because the chart control is so flexible, we have split the different use cases into
separate sections.

- [Basic concepts](charts/basics.md)
- [Line charts](charts/line.md)
- [Bar charts](charts/bar.md)
- [Scatter charts](charts/scatter.md)
- [Others features](charts/others.md)
