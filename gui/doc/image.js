/**
 * A image control that can trigger a function when pressed.
 *
 * @element image
 */
class image extends shared {
    /**
     * the image
     * @type {dynamic(url | path | file), default property}
     */
    content;

    /**
     * the image label
     * @type {dynamic(str)}
     */
    label;

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:<ul><li>gui instance</li><li>id</li><li>action</li></ul>
     * @type {str}
     */
    on_action = "";

    /**
     * The HTML component width.<br/>(CSS property)
     * @type {str|int|float}
     */
    width = "300px";

    /**
     * The HTML component height.<br/>(CSS property)
     * @type {str|int|float}
     */
    height;
}
