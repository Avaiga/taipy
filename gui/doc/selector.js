/**
 * A control that allows for selecting items from a list of choices.
 * 
 * Each item is represented by a string, an image or both.
 *
 * The selector can let the user select multiple items.
 * 
 * A filtering feature is available to display only a subset of the items.
 *
 * You can use an arbitrary type for all the items (see the [example](#binding-to-a-list-of-objects)).
 *
 * @element selector
 */
class selector extends lovComp {

    /**
     * Combines the control with a filter input area.
     *
     * @type {bool}
     */
    filter = false;

    /**
     * Allows for multiple selection.
     *
     * @type {bool}
     */
    multiple = false;

    /**
     * The width of this control.<br/>This must be a CSS measurement.
     *
     * @type {str|int}
     */
     width = 360

    /**
     * The height of this control.<br/>This must be a CSS measurement.
     *
     * @type {str|int}
     */
    height
}
