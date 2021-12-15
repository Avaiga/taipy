/**
 * Organizes its children into cells in a regular grid.
 * 
 * block component
 *
 * ## Usage
 * ### Simple
 * <code><|layout|<br>...<br>|></code>
 * ### Advanced
 * <code><|layout|columns=1 1|gap=1rem|<br>...<br>|></code>
 * <br>or with properties<br>
 * <code><|layout|properties={properties}|<br>...<br>|></code>
 * <br>or with closing tag<br>
 * <code><|layout.start|...|><br>...<br><|layout.end|></code>
 * @element layout
 * @prop columns[mobile]
 */
class layout extends shared {

    /**
     * The list of each column's weight
     * 
     * For example, `"1 2"` creates a grid which is 2 columns wide:
     * 
     *   - 1fr
     *   - 2fr
     * 
     * @type {str, default property}
     */
     columns = "1 1";

    /**
     * The list of each column's weight, when displayed on a mobile device.
     *
     * @attr columns[mobile]
     * @type {str}
     */
     columns_mobile_ = "1";

    /**
     * The distance between the columns.
     * 
     * The value uses the CSS units.
     * @type {str}
     */
    gap = "0.5rem";
}
