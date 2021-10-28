/**
 * button component displays a button that triggers an function

 * ## Usage
 * ### Simple 
 * <code><|Button Label|button|></code>
 * ### Advanced 
 * <code><|Button Label|button|on_action=button_action_function_name|></code>
 * <br>or with properties<br>
 * <code><|Button Label|button|properties={properties}|></code>
 * @element button
 */
class button extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * the button label
     * @type {str, default property}
     */
     label;

    /**
     * binded to a dictionnary that contains the component attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-button";

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:<ul><li>gui instance</li><li>id</li><li>action</li></ul>
     * @type {str}
     */
    on_action = ""

}