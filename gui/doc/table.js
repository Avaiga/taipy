/**
 * Table component supports 3 display modes:
 * <ul>
 * <li> paginated where you can choose the page size and page size options (allow_all_rows add an option to show a page with all rows)</li>
 * <li> unpaginated where all rows and no pages are shown (show_all = True)</li>
 * <li> auto-loading where the pages are loading on demand depending on teh scrolling</li>
 * </ul>
 * 
 * ## Usage
 * ### Simple 
 * <code><|{value}|table|></code>
 * ### Advanced 
 * <code><|{value}|table|page_size=10|page_size_options=10;30;100|columns=Col 1;Col 2;Col 3|date_format=eee dd MMM yyyy|not allow_all_rows|show_all=No|auto_loading=False|width=100vw|height=100vw|selected={selection}|propagate|></code>
 * <br>or with properties<br>
 * <code><|{value}|table|properties={properties}|selected={selection}|></code>
 * @element table
 */
class table extends HTMLElement {

    /**
     * an id that will be assign the main HTML component
     * @type {str}
     */
     id;
     
    /**
     * binded to a dataframe
     * @type {binded(any), default property}
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
    class_name = "taipy-table";

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