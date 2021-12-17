/**
 * A control that can display or set a formatted date, with or without time.
 *
 * @element date_selector
 */
class date_selector extends propagate {

     /**
     * bound to a date
     * @type {dynamic(datetime), default property}
     */
     date;

    /**
     * shows the time part of the date
     * @type {bool}
     */
     with_time = false;

}
