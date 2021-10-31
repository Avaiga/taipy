class lovComp extends propagate {

    /**
     * bound to the selection value
     * @type {dynamic(any), default property}
     */
    value;

    /**
     * list of elements
     * @type {dynamic(str|List[str|TaipyImage|any])}
     */
    lov;

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