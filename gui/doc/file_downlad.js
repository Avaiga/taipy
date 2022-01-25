/**
 * A file_download control that allows to download files automagically or by clicking on a button.
 *
 * @element file_download
 */
class file_download extends shared {
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
     * name of a function that will be triggered when the download is initiated.<br> parameters of that function are all optional:<ul><li>gui instance</li><li>id</li><li>action</li></ul>
     * @type {str}
     */
    on_action;

    /**
     * download the file as soon as the page is loaded
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
