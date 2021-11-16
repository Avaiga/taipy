/**
 * a list component that allows multiple selection and filtering on label<br>text and image can be used

 * ## Usage
 * ### Simple
 * <code><|{value}|selector|lov=Item 1;Item 2;Item 3|></code>
 * ### Advanced
 * <code><|{value}|selector|lov={lov}|no filter|not multiple|type=myType|adapter=lambda x: (x.id, x.name)|></code>
 * <br>or with properties<br>
 * <code><|{value}|selector|properties={properties}|lov={lov}|></code>
 * @element selector
 */
class selector extends lovComp {

    /**
     * allows a text filtering input
     * @type {bool}
     */
    filter = false;

    /**
     * Multiple selection
     * @type {bool}
     */
    multiple = false;

}
