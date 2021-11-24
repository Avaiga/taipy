/**
 * part component displays its children in a block
 * <br>part can be simplified by specifying no component
 *
 * ## Usage
 * ### Simple
 * <code><|<br>...<br>|></code>
 * ### Advanced
 * <code><|part|class_name=name|not render|<br>...<br>|></code>
 * <br>or with closing tag<br>
 * <code><|part.start|...|><br>...<br><|part.end|></code>
 * @element part
 */
class part extends shared {

     /**
      * nothing will be display if false.
      * @type {dynamic(bool)}
      */
      render = true;
}
