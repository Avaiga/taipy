/**
 * A side pane.
 *
 * TODO: Complete
 * block component
 *
 * ## Usage
 * ### Simple
 * <code><|{open}|pane|</code>
 * 
 * ...
 * 
 * <code>|></code>
 * ### Advanced
 * <code><|pane|open={value}|page_id=page1|close_action=close_action|></code>
 * 
 * or with properties
 * 
 * <code><|{open}|pane|properties={properties}|partial={myPartial}|></code>
 * @element pane
 */
class pane extends shared {

     /**
     * shows the pane
     * @type {bool, default property}
     */
     open

    /**
     * name of a function that will be triggered on close (click outside or Esc).<ul>Parameters of that function are all optional:<li>gui instance</li><li>id</li><li>action</li></ul>if close_action is empty, no function is called
     * @type {str}
     */
     close_action

    /**
     * a Partial object that holds the content of the pane<br>should not be defined if page_id is set
     * @type {Partial}
     */
     partial

     /**
      * a page id to show as the content of the pane<br>should not be defined if partial is set
      * @type {str}
      */
     page_id

     /**
      * width of the pane (if anchor is left or right)
      * 
      * @type {str}
      */
      width = "30vw"

     /**
      * height of the pane (if anchor is top or bottom)
      * 
      * @type {str}
      */
      height = "30vh"

     /**
      * anchor of the pane<ul>values:<li>left</li><li>right</li><li>top</li><li>bottom</li></ul>
      * 
      * @type {str}
      */
     anchor = "left"

     /**
      * is the pane in the document or over it
      * 
      * @type {bool}
      */
     persistent = false
}
