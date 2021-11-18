/**
 * layout component displays its children in a grid
 *
 * ## Usage
 * ### Simple
 * <code><|layout|<br>...<br>|></code>
 * ### Advanced
 * <code><|layout|type=1 1|gap=1rem|<br>...<br>|></code>
 * <br>or with properties<br>
 * <code><|layout|properties={properties}|<br>...<br>|></code>
 * <br>or with closing tag<br>
 * <code><|layout.start|...|><br>...<br><|layout.end|></code>
 * @element layout
 */
class layout extends shared {

    /**
     * describe the weight of each column <br> ie "1 2" will create a grid with 2 columns of width:<br> - 33%<br> - 66%
     * @type {str, default property}
     */
    type = "1 1";

    /**
     * prevent from hiding the children if true
     * @type {str}
     */
    gap = "0.5rem";
}
