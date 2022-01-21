/**
 * A file_selector control that allows to upload files by selection or drop.
 *
 * @element file_selector
 */
class file_selector extends shared {
    /**
     * the image
     * @type {dynamic(url | path | file), default property}
     */
    content;

    /**
     * the button label
     * @type {dynamic(str)}
     */
    label;

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:<ul><li>gui instance</li><li>id</li><li>action</li></ul>
     * @type {str}
     */
    on_action;

    /**
     * download the file as s0on as the page is loaded
     * @type {bool}
     */
    auto = false;

    /**
     * nothing will be displayed if false.
     * @type {dynamic(bool)}
     */
    render = true;

    /**
     * always downbload the file, allows the browser to show the content in a different tab if false.
     * @type {bool}
     */
    bypass_preview = true;

    /**
     * proposed name of the file to save
     * @type {str}
     */
    name;
}
