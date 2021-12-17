/**
 * A button control that can trigger a function when pressed.
 *
 * @element button
 */
class button extends shared {

     /**
     * the button label
     * @type {str, default property}
     */
     label;

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:<ul><li>gui instance</li><li>id</li><li>action</li></ul>
     * @type {str}
     */
    on_action = ""

}
