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
class selector extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

     /**
     * binded to the selection value
     * @type {binded(any), default property}
     */
     value;

    /**
     * binded to a dictionnary that contains the component attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-selector";

    /**
     * list of elements
     * @type {str|List[str|TaipyImage|any]}
     */
     lov;

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

    /**
     * function that transforms an element of the lov into a tuple(id:str, label:str|TaipyImage)
     * @type {FunctionType}
     */
     adapter = "lambda x: str(x)";

    /**
     * needed if the lov List contains a non specific type of data (ex: dict)<br> value and lov varaibales are associated with this type and the adapter<br>
     * @type {str}
     */
    type = "Type(lov-element)";

    /**
     * allows the value to be automatically propagated.<br>default value is defined at the app config level 
     * @type {bool}
     */
     propagate = "App config";
    }