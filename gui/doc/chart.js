/**
 * Chart component (based on [plotly.js](https://plotly.com/javascript/))
 * <br>Indexed properties can have a default value (referenced by *property_name*) which would be overridden by the indexed propety ((referenced by *property_name[index]* with index starting at 1))
 * @element chart
 */
class chart extends HTMLElement {
    /**
     * binded to a dataframe
     * @type {binded(any)}
     */
    value;

    /**
     * binded to a dictionnary that contains the componenet attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-chart chart";

    /**
     * component id
     * @type {str}
     */
    id;

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
     * Should change on binded variables be propagated automatically
     * @type {bool}
     */
    propagate = true;

    /**
     * List of selected indices
     * @type {binded(list[int]|str)}
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
