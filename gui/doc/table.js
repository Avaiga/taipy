/**
 * Displays a data set as tabular data.
 *
 * The table component supports 3 display modes:
 *
 *   - _paginated_: you can choose the page size and page size options (allow_all_rows add an option to show a page with all rows).
 *   - _unpaginated_:  all rows and no pages are shown (`show_all = True`).
 *   - _auto-loading_: the pages are loaded on demand depending on the visible area.
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
class table extends shared {
    /**
     * bound to a data object
     * @type {any, default property}
     */
    value;

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
    width = "100vw";

    /**
     * HTML component height (CSS property)
     * @type {str|int|float}
     */
    height = "80vh";

    /**
     * List of selected indices
     * @type {list[int]|str}
     */
    selected;

    /**
     * List of page sizes
     * @type {List[int]|str}
     */
    page_size_options = [50, 100, 500];

    /**
     * List of column names <br><ul><li>*str* ; separated list </li><li>*List[str]* </li><li>*dict* <pre>{"col name": {format: "format", index: 1}}</pre>if index is specified, it represents the display order of the columns <br>if not, the list order defines the index</li></ul>
     * @type {str|List[str]|Dict[str, Dict[str, str|int]]}
     */
    columns = "All columns";

    /**
     * Date format for all date columns when format is not defined
     * @type {str}
     */
    date_format = "MM/dd/yyyy";

    /**
     * Number format for all number columns when format is not defined <br>format is printf compatible
     * @type {str}
     */
    number_format;

    /**
     * Column name indexed property (group_by[column name]) that indicates that the column can be aggregated
     * @type {column_indexed(bool)}
     */
    group_by;

    /**
     * Column name indexed property (applly[column name]) where the value is the name of an aggregation function (built-in functions are count, sum, mean, median, min, max, std, first, last). A local function or lambda can also be provided, it should take a serie as parameter and return a scalar value
     * @type {column_indexed(str)}
     */
    apply;

    /**
     * Column name indexed property (applly[column name]) where the value is a local function or lambda, it should take at least a serie as parameter (with column_name and function_name optional string patameters) and return a string value
     * @type {column_indexed(str)}
     */
    style;
}
