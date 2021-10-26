/**
 * Description of table element
 * @element table
 */
class table extends HTMLElement {

    /**
     * binded to a dataframe
     * @type {binded(any)}
     */
    value;

    /**
     * binded to a dictionnary that contains the componenet attributes
     * @type {dict[str, any]}
     */
    properties;

    /**
     * css class name that will be associated to the main HTML Element
     * @type {str}
     */
    class_name = "taipy-table table";

    /**
     * when table is paginated or auto-loaded, number of rows in each page
     * @type {int}
     */
    page_size = 100;

    /**
     * Allow a page size for all rows
     * @type {bool}
     */
     allow_all_rows = false;

    /**
     * non paginated table
     * @type {bool}
     */
     show_all = false;

     /**
     * data will be loaded on demand
     * @type {bool}
     */
     auto_loading = false;

    /**
     * HTML component width (CSS property)
     * @type {str|int|float}
     */
     width = "100vw"

    /**
     * HTML component height (CSS property)
     * @type {str|int|float}
     */
     height = "100vw"

    /**
     * Should change on binded variables be propagated automatically
     * @type{bool}
     */
    propagate = true;

    /**
     * List of selected indices
     * @type {binded(list[int]|str)}
     */
    selected;

    /**
     * List of page sizes
     * @type {List[int]|str}
     */
    page_size_options = [50, 100, 500];

    /**
     *  List of column names <br><ul><li>*str* ; separated list </li><li>*List[str]* </li><li>*dict* <pre>{"col name": {format: "format", index: 1}}</pre>if index is specified, it represents the display order of the columns <br>if not, the list order defines the index</li></ul>
     * @type {str|List[str]|dict[str, dict[str, str|int]]}
     */
    columns = "All columns";

    /**
     * date format for all date columns when format is not defined
     * @type {str}
     */
    date_format = "MM/dd/yyyy";

    /**
     * number format for all number columns when format is not defined <br>format is printf compatible
     * @type {str}
     */
    number_format;
}