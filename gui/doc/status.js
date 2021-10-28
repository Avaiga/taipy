/**
 * status component displays a status or a list of statuses
 * value can be a list of or a single dict containing the keys
 * <ul><li>status</li><li>message</li></ul>
 
 * ## Usage
 * ### Simple 
 * <code><|{value}|status|></code>
 * ### Advanced 
 * <code><|{value}|status|></code>
 * <br>or with properties<br>
 * <code><|{value}|status|properties={properties}|></code>
* @element status
 */
class status extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

    /**
     * binded to a value
     * @type {binded(dict|list[dict]), default property}
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
    class_name = "taipy-status";

}