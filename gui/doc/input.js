/**
 * input component display an input field

 * ## Usage
 * ### Simple 
 * <code><|{value}|input|></code>
 * ### Advanced 
 * <code><|{value}|input|></code>
 * <br>or with properties<br>
 * <code><|{value}|input|properties={properties}|></code>
 * @element input
 */
class input extends HTMLElement {

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
    class_name = "taipy-input";

    /**
     * allows the value to be automatically propagated.<br>default value is defined at the app config level 
     * @type {bool}
     */
     propagate = "App config";

}