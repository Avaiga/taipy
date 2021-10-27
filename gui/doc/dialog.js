/**
 * dialog component displays a modal dialog
 * @element dialog
 */
class dialog extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * shows the dialog
     * @type {str}
     */
     open;

    /**
     * binded to a dictionnary that contains the component attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-dialog";

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:
     * <ul><li>gui instance</li><li>id</li><li>action</li></ul>if cancel_action is empty, the button is not shown
     * @type {str}
     */
     cancel_action = ""

    /**
     * text of the cancel button
     * @type {str}
     */
     cancel_action_text = "Cancel"

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:
     * <ul><li>gui instance</li><li>id</li><li>action</li></ul>
     * @type {str}
     */
     validate_action = "validate"

    /**
     * text of the validate button
     * @type {str}
     */
     validate_action_text = "Validate"

    /**
     * a Partial object that holds the content of the dialog<br>should not be defined if page_id is set
     * @type {Partial}
     */
     partial

     /**
      * a page id to show as the content of the dialog<br>should not be defined if partial is set
      * @type {str}
      */
     page_id

}