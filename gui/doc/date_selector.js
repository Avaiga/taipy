/**
 * date_selector component display a formatted date/time selector
 * @element date_selector
 */
class date_selector extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * binded to a value
     * @type {str}
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
    class_name = "taipy-date-selector";

    /**
     * shows the time part of the date
     * @type {bool}
     */
     with_time = false;

    }