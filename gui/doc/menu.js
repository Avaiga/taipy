/**
 * A menu control.
 *
 * This control is represented by a unique left-anchor and foldable vertical menu.
 *
 * ## Usage
 * ### Simple
 * <code><|menu|lov={["menu 1", "menu 2"]}></code>
 * ### Advanced
 * <code><|menu|lov={lov}|label=a label|width=15vw|width[mobile]=85vw|inactiveIds={ids}|></code>
 * @element menu
 */
class menu {
    /**
     * The list of values.
     *
     * @type {dynamic(str|List[str|TaipyImage|any]), default property}
     */
    lov;

    /**
     * The function that transforms an element of _lov_ into a _tuple(id:str, label:str|TaipyImage)_.
     *
     * @type {FunctionType}
     */
    adapter = "lambda x: str(x)";

    /**
     * Must be specified if `lov` contains a non specific type of data (ex: dict).<br/>_value_ must be of that type, _lov_ must be an iterable on this type, and the adapter function will receive an object of this type.
     *
     * @type {str}
     */
    type = "Type(lov-element)";

    /**
     * Menu title.
     *
     * @type {str}
     */
    label;

    /**
     * menu width when unfolded on a non-mobile device.
     *
     * @type {str}
     */
    width = "15vw";

    /**
     * menu width when unfolded on a mobile device.
     * @attr width[mobile]
     * @type {str}
     */
    width_mobile_ = "85vw";

    /**
     * Indicats if this component is active.<br/>An inactive component provides no user interaction.
     *
     * @type {dynamic(bool)}
     */
    active = true;

    /**
     * name of a function that will be triggered.<br> parameters of that function are all optional:<ul><li>gui instance</li><li>id</li><li>action</li><li>payload with selected id</li></ul>
     * @type {str}
     */
    on_action = "on_menu_action";
}
