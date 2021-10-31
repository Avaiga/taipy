/**
 * slider component displays a range input allowing to select an integer value between min and max by sliding a cursor

 * ## Usage
 * ### Simple 
 * <code><|{value}|slider|></code>
 * ### Advanced 
 * <code><|{value}|slider|min=1|max=100|propagate|></code>
 * <br>or with properties<br>
 * <code><|{value}|slider|properties={properties}|></code>
 * @element slider
 */
class slider extends HTMLElement {

    /**
     * bound to a value
     * @type {dynamic(int|float), default property}
     */
    value;

    /**
     * minimum value
     * @type {int|float}
     */
    min = 1;
    
    /**
     * maximum value
     * @type {int|float}
     */
    max = 100;

}