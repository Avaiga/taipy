/**
 * field component is the simplest component. It displays a value as text. (the component name is not mandatory)
 * <pre><|{value}|></pre> is equivalent to <pre><|{value}|field|></pre>
 * @element field
 */
class field extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;

    /**
     * binded to a value
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
    class_name = "taipy-field";

    /**
     * format for the value<br> depending of the type of the value, we support<ul><li>date/time formatting</li><li>number formatting (printf syntax)</li></ul>
     */
    format

}