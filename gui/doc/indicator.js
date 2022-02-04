/**
 * Displays a label on a red to green scale at a specific position.
 * Min can be > Max.
 * value will be kept inside min, max
 * 
 * @element indicator
 */
class indicator extends shared {

    /**
     * Label to display. Can be formatted if is numeric.
     * @type {dynamic(any), default property}
     */
     display;

    /**
     * Position of the label.
     * @type {dynamic(int,float)}
     */
     value = min;

    /**
     * Minimum value.
     * @type {(int,float)}
     */
     min = 0;

    /**
     * Maximum value.
     * @type {(int,float)}
     */
     max = 100;

     /**
     * format for the value.<br>printf syntax.
     */
    format;

}
