/**
 * a tree component that allows multiple selection and filtering on label<br>text and image can be used

 * ## Usage
 * ### Simple
 * <code><|{value}|tree|lov=Item 1;Item 2;Item 3|></code>
 * ### Advanced
 * <code><|{value}|tree|lov={lov}|no filter|not multiple|type=myType|adapter=lambda x: (x.id, x.name, x.children)|></code>
 * <br>or with properties<br>
 * <code><|{value}|selector|properties={properties}|lov={lov}|></code>
 * @element tree
 */
class tree extends selector {

}
