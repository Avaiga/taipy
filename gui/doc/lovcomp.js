class lovComp extends propagate {

    /**
     * Bound to the selection value.
     * @type {dynamic(any), default property}
     */
    value;

    /**
     * The list of values.
     * @type {dynamic(str|List[str|TaipyImage|any])}
     */
    lov;

    /**
     * The function that transforms an element of `lov` into a `tuple(id:str, label:str|TaipyImage)`.
     * @type {FunctionType}
     */
    adapter = "lambda x: str(x)";

    /**
     * Must be specified if `lov` contains a non specific type of data (ex: dict).
     * 
     * `value` and `lov` are associated with this type and the adapter.
     * @type {str}
     */
    type = "Type(lov-element)";

}
