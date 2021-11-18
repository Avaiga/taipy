/**
 * expandable component displays its children in a collapsable zone
 *
 * ## Usage
 * ### Simple
 * <code><title|expandable|<br>...<br>|></code>
 * ### Advanced
 * <code><{value}|expandable|expanded={False}|<br>...<br>|></code>
 * <br>or with properties<br>
 * <code><|expandable|properties={properties}|<br>...<br>|></code>
 * <br>or with closing tag<br>
 * <code><|expandable.start|...|><br>...<br><|expandable.end|></code>
 * @element expandable
 */
class expandable extends shared {

    /**
     * title, bound to a value
     * @type {str, default property}
     */
     value;

    /**
     * opened or closed
     * @type {bool}
     */
    expanded = true;
}
