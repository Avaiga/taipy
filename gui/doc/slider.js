/**
 * Displays and allows the user to set a value within a range.
 * 
 * The range is set by the values `min` and `max` that must be integer values.
 *
 * ## Usage
 * ### Simple
 * <code><|{value}|slider|></code>
 * ### Advanced
 * <code><|{value}|slider|min=1|max=100|propagate|></code>
 * <br>or with properties<br>
 * <code><|{value}|slider|properties={properties}|></code>
 * @element slider
 */
class slider extends HTMLElement {

    /**
     * bound to a value
     * @type {dynamic(int|float), default property}
     */
    value;

    /**
     * minimum value
     * @type {int|float}
     */
    min = 1;

    /**
     * maximum value
     * @type {int|float}
     */
    max = 100;

}
