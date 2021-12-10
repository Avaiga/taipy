/**
 * A control that can display or set a formatted date, with or without time.

 * ## Usage
 * ### Simple
 * <code><|{value}|date_selector|></code>
 * ### Advanced
 * <code><|{value}|date_selector|not with_time|></code>
 * <br>or with properties<br>
 * <code><|{value}|date_selector|properties={properties}|></code>
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
