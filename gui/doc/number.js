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
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * binded to a value
     * @type {binded(any), default property}
     */
     value;

    /**
     * binded to a dictionnary that contains the component attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-number";

    /**
     * allows the value to be automatically propagated.<br>default value is defined at the app config level 
     * @type {bool}
     */
     propagate = "App config";
}