/**
 * field component is the simplest component. It displays a value as text. (the component name is not mandatory)
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
class field extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

    /**
     * a value
     * @type {any, default property}
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
    class_name = "taipy-field";

    /**
     * format for the value<br> depending of the type of the value, we support<ul><li>date/time formatting</li><li>number formatting (printf syntax)</li></ul>
     */
    format

}