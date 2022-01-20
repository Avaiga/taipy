/**
 * A file_selector control that allows to upload files by selection or drop.
 *
 * @element file_selector
 */
class file_selector extends shared {
    /**
     * the variable that will be updated with the path or list of path of the uploaded files.
     * @type {dynamic(str), default property}
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
     * allows multiple file upload
     * @type {bool}
     */
    multiple = false;

    /**
     * a list of the file extensions that can be uploaded.
     * @type {str}
     */
    extensions = ".csv,.xlsx";

    /**
     * message displayed when hovering with dragged file(s)
     * @type {str}
     */
    drop_message = "Drop here to Upload";
}
