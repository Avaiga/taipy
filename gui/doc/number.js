/**
 * A kind of [`input`](input.md) that handles numbers.

 * ## Usage
 * ### Simple
 * <code><|{value}|number|></code>
 * ### Advanced
 * <code><|{value}|number|class_name=style_class_name|></code>
 * <br>or with properties<br>
 * <code><|{value}|number|properties={properties}|></code>
 * @element number
 */
class numberCls extends HTMLElement {

    /**
     * Bound to a numeric value.
     * @type {dynamic(any), default property}
     */
    value;

}
