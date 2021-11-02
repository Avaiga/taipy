/**
 * Chart component (based on [plotly.js](https://plotly.com/javascript/))
 * <br>Indexed properties can have a default value (referenced by *property_name*) which would be overridden by the indexed propety ((referenced by *property_name[index]* with index starting at 1))

 * ## Usage
 * ### Simple 
 * <code><|{value}|chart|x=Col 1|y=Col 2|></code>
 * ### Advanced 
 * <code><|{value}|chart|x=Col 1|selected_color=green|y[1]=Col 2|label[1]=Col 3|y[2]=Col 4|label[2]=Col 5|mode[2]=markers|color[2]=red|type[2]=scatter|xaxis[2]=x2|layout={subplot_layout}|range_change=range_change|width=100%|height=100%|selected={selection}|></code>
 * <br>or with properties<br>
 * <code><|{value}|chart|properties={properties}|selected={selection}|></code>
 * @element chart
 */
class chart extends shared {
    /**
     * bound to a data object
     * @type {any, default property}
     */
    value;

    /**
     * chart title
     * @type {str}
     */
    title;

    /**
     * HTML component width (CSS property)
     * @type {str|int|float}
     */
    width = "100vw";

    /**
     * HTML component height (CSS property)
     * @type {str|int|float}
     */
    height = "100vw";

    /**
     * List of selected indices
     * @type {dynamic(list[int]|str)}
     */
    selected;

    /**
     * plotly.js compatible [layout object](https://plotly.com/javascript/reference/layout/)
     * @type {dict[str, any]}
     */
    layout;

    /**
     * callback function called on zoom with parameter <ul><li>id: optional[str]</li><li>action: optional[str]</li><li>payload: dict[str, any] as emmitted by [plotly](https://plotly.com/javascript/plotlyjs-events/#update-data)</li></ul>
     * @type {function name}
     */
    range_change;

    /**
     *  List of column names <br><ul><li>*str* ; separated list </li><li>*List[str]* </li><li>*dict* <pre>{"col name": {format: "format", index: 1}}</pre>if index is specified, it represents the display order of the columns <br>if not, the list order defines the index</li></ul>
     * @type {str|List[str]|dict[str, dict[str, str]]}
     */
    columns = "All columns";

    /**
     * column name for hover text
     * @type {indexed(str)}
     */
     label;

     /**
     * column name for z axis
     * @type {indexed(str)}
     */
     z;

     /**
     * column name for y axis
     * @type {indexed(str)}
     */
     y;

     /**
     * column name for x axis
     * @type {indexed(str)}
     */
    x;

    /**
     * chart [mode](https://plotly.com/javascript/reference/scatter/#scatter-mode)
     * @type {indexed(str)}
     */
    mode = "lines+markers";

    /**
     * chart [type](https://plotly.com/javascript/reference/)
     * @type {indexed(str)}
     */
    type;

    /**
     * trace marker color
     * @type {indexed(str)}
     */
    color;

    /**
     * x axis id
     * @type {indexed(str)}
     */
    xaxis = "x";

    /**
     * y axis id
     * @type {indexed(str)}
     */
    yaxis = "y";

    /**
     * trace marker color
     * @type {indexed(str)}
     */
    color;

    /**
     * trace selected marker color
     * @type {indexed(str)}
     */
    selected_color;

    /**
     * trace [marker](https://plotly.com/javascript/reference/scatter/#scatter-marker)
     * @type {indexed(dict[str, any])}
     */
    marker;

    /**
     * trace [selected marker](https://plotly.com/javascript/reference/scatter/#scatter-selected-marker)
     * @type {indexed(dict[str, any])}
     */
    selected_marker;
}
