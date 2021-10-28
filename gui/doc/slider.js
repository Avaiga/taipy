/**
 * slider component displays a range input allowing to select an integer value between min and max by sliding a cursor

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
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * binded to a value
     * @type {binded(int), default property}
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
    class_name = "taipy-slider";

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
     min = 1;
    
    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    max = 100;

    /**
     * allows the value to be automatically propagated.<br>default value is defined at the app config level 
     * @type {bool}
     */
    propagate = "App config";
}