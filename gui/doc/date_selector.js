/**
 * date_selector component displays a formatted date/time selector

 * ## Usage
 * ### Simple 
 * <code><|{value}|date_selector|></code>
 * ### Advanced 
 * <code><|{value}|date_selector|not with_time|></code>
 * <br>or with properties<br>
 * <code><|{value}|date_selector|properties={properties}|></code>
 * @element date_selector
 */
class date_selector extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * binded to a date
     * @type {datetime, default property}
     */
     date;

    /**
     * binded to a dictionnary that contains the component attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-date-selector";

    /**
     * shows the time part of the date
     * @type {bool}
     */
     with_time = false;

    /**
     * allows the value to be automatically propagated.<br>default value is defined at the app config level 
     * @type {bool}
     */
     propagate = "App config";

}