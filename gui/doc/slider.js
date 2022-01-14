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
     */
    text_anchor = "bottom"

}
