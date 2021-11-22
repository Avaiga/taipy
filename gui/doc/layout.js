/**
 * layout component displays its children in a grid
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
     * list of each column's weight<br> ie "1 2" will create a grid with 2 columns of width:<br> - 33%<br> - 66%
     * @type {str, default property}
     */
     columns = "1 1";

    /**
     * list of each column's weight for mobile devices
     * @attr columns[mobile]
     * @type {str}
     */
     columns_mobile_ = "1";

    /**
     * distance between the columns
     * @type {str}
     */
    gap = "0.5rem";
}
