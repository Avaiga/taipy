class shared extends HTMLElement {
    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
    id;

    /**
     * binded to a dictionnary that contains the component attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element<br>These class names will be added to a standard <code>taipy-&lt;component name&gt;</code>.
     * @type {str}
     */
    class_name;
 
}