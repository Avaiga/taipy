/**
 * Displays its children in a block.
 * 
 * block component
 * 
 * Part controls can be simplified by specifying no component. TODO: explain.
  *
 * ## Usage
 * ### Simple
 * <code><|<br>...<br>|></code>
 * ### Advanced
 * <code><|part|class_name=name|don't render|<br>...<br>|></code>
 * <br>or with closing tag<br>
 * <code><|part.start|...|><br>...<br><|part.end|></code>
 * @element part
 */
class part extends shared {

     /**
      * nothing will be displayed if false.
      * @type {dynamic(bool)}
      */
      render = true;
}
