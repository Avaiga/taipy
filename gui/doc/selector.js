/**
 * a list component that allows multiple selection and filtering on label<br>text and image can be used
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
     * @type {binded(any)}
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
     * css class name that will be associated to the main HTML Element
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

    }