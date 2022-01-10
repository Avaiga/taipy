/**
 * Displays data sets in a chart or a group of charts.
 * 
 * The chart control is based on the [plotly.js](https://plotly.com/javascript/)
 * graphs library.
 *
 * A chart control can hold several traces, that can display individual data sets.  
 * To indicate properties for a given trace, you will use the indexed properties
 * (using the *property_name[index]* syntax, with the indices starting at index 1) to
 * specify which trace you target.  
 * Indexed properties can have a default value (using the *property_name* syntax with
 * no index) which is overridden by any specified indexed property.
 * 
 * @element chart
 */
class chart extends shared {
    /**
     * The data object bound to this chart control.
     * @type {any, default property}
     */
    value;

    /**
     * The title of this chart control.
     * @type {str}
     */
    title;

    /**
     * The HTML component width.<br/>(CSS property)
     * @type {str|int|float}
     */
    width = "100vw";

    /**
     * The HTML component height.<br/>(CSS property)
     * @type {str|int|float}
     */
    height = "100vw";

    /**
     * List of the selected point indices.
     * @type {dynamic(list[int]|str)}
     */
    selected;

    /**
     * The _plotly.js_ compatible [layout object](https://plotly.com/javascript/reference/layout/).
     * @type {dict[str, any]}
     */
    layout;

    /**
     * Callback function called when the visible part of the x axis changes.<br/>The function receives three parameters:<ul><li>`id` (optional[str]): the identifier of the chart control.</li><li>`action` (optional[str]): the name of the action that provoked the change.</li><li>`payload` (dict[str, any]): all the event information, as emmitted by</li> [plotly](https://plotly.com/javascript/plotlyjs-events/#update-data)</li></ul>
     *
     * @type {function name}
     */
    range_change;

    /**
     *  List of column names <br><ul><li>*str*: ;-separated list of names</li><li>*List[str]*: list of names</li><li>*dict*: <pre>{"col_name": {format: "format", index: 1}}</pre>if index is specified, it represents the display order of the columns.<br/>If not, the list order defines the index</li></ul>
     * @type {str|List[str]|dict[str, dict[str, str]]}
     */
    columns = "All columns";

    /**
     * The label for a trace</br/>This is used when the mouse hovers over a trace.
     * @type {indexed(str)}
     */
     label;

    /**
     * The name of a trace.
     * @type {indexed(str)}
     */
     name;

    /**
     * The orientation of a trace.
     * @type {indexed(str)}
     */
     orientation;

    /**
     * Column name for the _z_ axis.
     * @type {indexed(str)}
     */
     z;

    /**
     * Column name for the _y_ axis.
     * @type {indexed(str)}
     */
     y;

    /**
     * Column name for _x_ axis.
     * @type {indexed(str)}
     */
    x;

    /**
     * Column name for the text associated to the point (mode with _text_).
     * @type {indexed(str)}
     */
    text;

    /**
     * Position of the text relative to the point (values: top, bottom, left, right)
     * @type {indexed(str)}
     */
    textposition;

    /**
     * Chart mode<br/>See the Plotly [chart mode](https://plotly.com/javascript/reference/scatter/#scatter-mode) documentation for details.
     * @type {indexed(str)}
     */
    mode = "lines+markers";

    /**
     * Chart type<br/>See the Plotly [chart type](https://plotly.com/javascript/reference/) documentation for details.
     * @type {indexed(str)}
     */
    type;

    /**
     * The color of the indicated trace.
     * @type {indexed(str)}
     */
    color;

    /**
     * The _x_ axis identifier.
     * @type {indexed(str)}
     */
    xaxis = "x";

    /**
     * The _y_ axis identifier.
     * @type {indexed(str)}
     */
    yaxis = "y";

    /**
     * The color of the selected points for a trace.
     * @type {indexed(str)}
     */
    selected_color;

    /**
     * The type of markers used for a trace.<br/> See [marker](https://plotly.com/javascript/reference/scatter/#scatter-marker) for details.
     * @type {indexed(dict[str, any])}
     */
    marker;

    /**
     * The configuration of line used for a trace.<br/> See [line](https://plotly.com/javascript/reference/scatter/#scatter-line) for details. if str then dash
     * @type {indexed(str|dict[str, any])}
     */
     line;

     /**
     * The type of markers used for selected points in a trace<br/>See [selected marker](https://plotly.com/javascript/reference/scatter/#scatter-selected-marker) for details.
     * @type {indexed(dict[str, any])}
     */
    selected_marker;
}
