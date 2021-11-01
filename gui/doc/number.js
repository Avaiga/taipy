/**
 * number component displays an input field that handle numbers

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
     * bound to a numeric value
     * @type {dynamic(any), default property}
     */
    value;

}