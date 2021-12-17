class shared extends HTMLElement {
    /**
     * The identifier that will be assigned to the rendered HTML component.
     * @type {str}
     */
    id;

    /**
     * Bound to a dictionary that contains the component properties.
     * @type {dict[str, any]}
     */
    properties;

    /**
     * CSS class name that will be associated to the generated HTML Element<br/>This class names will be added to the default <code>taipy-&lt;component_type&gt;</code>.
     * @type {str}
     */
    class_name;

}
