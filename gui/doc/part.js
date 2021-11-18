/**
 * part component displays its children in a block
 * <br>part can be simplified by specifying no component
 *
 * ## Usage
 * ### Simple
 * <code><|<br>...<br>|></code>
 * ### Advanced
 * <code><|part|class_name=name|<br>...<br>|></code>
 * <br>or with closing tag<br>
 * <code><|part.start|...|><br>...<br><|part.end|></code>
 * @element part
 */
class part extends shared {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
      * css class name that will be associated to the main HTML Element<br>These class names will be added to a standard <code>taipy-&lt;component name&gt;</code>.
      * @type {str}
      */
     class_name;
 
}
