/**
 * Displays and allows the user to set a value within a range.
 *
 * The range is set by the values `min` and `max` that must be integer values.
 * In case of a lov attribute, the slider can select between the different values
 *
 * @element slider
 */
class slider extends lovComp {
    /**
     * bound to a value.
     * @type {dynamic(int | float | str), default property}
     */
    value;

    /**
     * minimum value. Ignored when lov is defined.
     * @type {int|float}
     */
    min = 1;

    /**
     * maximum value. Ignored when lov is defined.
     * @type {int|float}
     */
    max = 100;

    /**
     * when a lov is defined, position of the selected label.<br>Possible values are <ul><li>bottom</li><li>top</li><li>left</li><li>right</li><li>none (no label displayed)</li></ul>
     *  @type {str}
     */
    text_anchor = "bottom";

    /**
     * labels for specific points of the slider. If true, use the labels of the lov if present. If a dict, key is lov id or index, value is label.
     * @type {bool|dict}
     */
    labels;

    /**
     * width of the HTML element
     *  @type {str}
     */
    width = "300px";

    /**
     * height of the HTML element (default to the width value when vertical orientation)
     *  @type {str}
     */
    height;

    /**
     * slider orientation vertical or horizontal (default)
     *  @type {"horizontal"|"vertical"}
     */
    orientation = "horizontal";
}
