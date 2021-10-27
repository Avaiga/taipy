/**
 * slider component displays a range input allowing to select an integer value between min and max by sliding a cursor
 * @element slider
 */
class slider extends HTMLElement {

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
    class_name = "taipy-slider";

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
     min = 1;
    
    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    max = 100;
}