/**
 * status component displays a status or a list of statuses
 * value can be a list of or a single dict containing the keys
 * <ul><li>status</li><li>message</li></ul>
 
 * ## Usage
 * ### Simple 
 * <code><|{value}|status|></code>
 * ### Advanced 
 * <code><|{value}|status|></code>
 * <br>or with properties<br>
 * <code><|{value}|status|properties={properties}|></code>
* @element status
 */
class status extends shared {

    /**
     * bound to a value
     * @type {dict|list[dict], default property}
     */
    value;

}