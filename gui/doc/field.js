/**
 * Displays a value as a static text.
 * 
 * Note that if order to create a `field` control, you don't need to specify the control name
 * in the text template. See the documentation for [Controls](../controls.md) for more details.
 *
 * ## Usage
 * ### Simple
 * <code><|{value}|></code>
 * ### Advanced
 * <code><|{value}|field|format=%.2f|></code>
 * <br>or with properties<br>
 * <code><|{value}|field|properties={properties}|></code>
 * @element field
 */
class field extends shared {

    /**
     * a value
     * @type {any, default property}
     */
    value;

    /**
     * format for the value<br> depending of the type of the value, we support<ul><li>date/time formatting</li><li>number formatting (printf syntax)</li></ul>
     */
    format

}
