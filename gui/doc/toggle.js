/**
 * a list component represented as a serie of toggle button
 * <br>text and image can be used
 * <br>theme boolean property shows a Theme toggle (light/dark)

 * ## Usage
 * ### Simple 
 * <code><|{value}|toggle|lov=Item 1;Item 2;Item 3|></code>
 * <br><code><|toggle|theme|></code>
 * ### Advanced 
 * <code><|{value}|toggle|lov={lov}|type=myType|adapter=lambda x: (x.id, x.name)|></code>
 * <br>or with properties<br>
 * <code><|{value}|toggle|properties={properties}|lov={lov}|></code>
 * @element toggle
 */
class toggle extends lovComp {

    /**
     * shows a Theme Toggle (light/dark)
     * @type {bool}
     */
    theme = false;

}