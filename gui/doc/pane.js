/**
 * A side pane.
 *
 * TODO: Complete
 * block component
 *
 * ## Usage
 * ### Simple
 * <code><|{value}|pane|></code>
 * ### Advanced
 * <code><|pane|open={value}|page_id=page1|close_action=close_action|></code>
 * 
 * or with properties
 * 
 * <code><|{value}|pane|properties={properties}|partial={myPartial}|></code>
 * @element dialog
 */
class pane extends shared {

     /**
     * shows the pane
     * @type {bool, default property}
     */
     open

    /**
     * name of a function that will be triggered on close (clieck outside or Esc).
     * 
     * Parameters of that function are all optional:
     * 
     * - gui instance
     * - id
     * - action
     * 
     * if close_action is empty, no function is called
     * @type {str}
     */
     close_action

    /**
     * a Partial object that holds the content of the pane
     * 
     * should not be defined if page_id is set
     * @type {Partial}
     */
     partial

     /**
      * a page id to show as the content of the pane
      * 
      * should not be defined if partial is set
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
      * anchor of the pane
      * 
      * values:
      * - left
      * - right
      * - top
      * - bottom
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
