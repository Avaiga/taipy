class lovComp extends propagate {

    /**
     * Bound to the selection value.
     *
     * @type {dynamic(any), default property}
     */
    value;

    /**
     * The list of values.
     *
     * @type {dynamic(str|List[str|TaipyImage|any])}
     */
    lov;

    /**
     * The function that transforms an element of _lov_ into a _tuple(id:str, label:str|TaipyImage)_.
     *
     * @type {FunctionType}
     */
    adapter = "lambda x: str(x)";

    /**
     * Must be specified if `lov` contains a non specific type of data (ex: dict).<br/>_value_ must be of that type, _lov_ must be an iterable on this type, and the adapter function will receive an object of this type.
     *
     * @type {str}
     */
    type = "Type(lov-element)";

}
