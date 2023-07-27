from ._init import *
from .gui_actions import download as download
from .gui_actions import get_module_context as get_module_context
from .gui_actions import get_module_name_from_state as get_module_name_from_state
from .gui_actions import get_state_id as get_state_id
from .gui_actions import get_user_content_url as get_user_content_url
from .gui_actions import hold_control as hold_control
from .gui_actions import invoke_callback as invoke_callback
from .gui_actions import invoke_long_callback as invoke_long_callback
from .gui_actions import navigate as navigate
from .gui_actions import notify as notify
from .gui_actions import resume_control as resume_control
from .icon import Icon as Icon
from .page import Page as Page
from .partial import Partial as Partial
from .renderers import BlockElementApi as BlockElementApi
from .renderers import ClassApi as ClassApi
from .renderers import ControlElementApi as ControlElementApi
from .renderers import Html as Html
from .renderers import Markdown as Markdown
from .state import State as State
from .utils import is_debugging as is_debugging

class text(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(self, value=..., raw=..., format=..., id=..., properties=..., class_name=..., hover_text=...) -> None:
        """
        Arguments:
            value (dynamic(any)): The value displayed as text by this control. (default: "")
            raw (bool): If set to True, the component renders as an HTML &lt;span&gt; element without any default style. (default: False)
            format (str): The format to apply to the value.<br/>See below.
            id (str): The identifier that will be assigned to the rendered HTML component.
            properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
            class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
            hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class button(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self, label=..., on_action=..., active=..., id=..., properties=..., class_name=..., hover_text=...
    ) -> None:
        """
                Arguments:
                    label (dynamic(str|Icon)): The label displayed in the button. (default: "")
                    on_action (Callback): The name of a function that is triggered when the button is pressed.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (optional[str]): the identifier of the button.</li>
        <li>action (optional[str]): the name of the action that provoked the change.</li>
        </ul>
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class input(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        value=...,
        password=...,
        label=...,
        multiline=...,
        lines_shown=...,
        change_delay=...,
        on_action=...,
        action_keys=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    value (dynamic(any)): The value represented by this control. (default: None)
                    password (bool): If True, the text is obscured: all input characters are displayed as an asterisk ('*'). (default: False)
                    label (str): The label associated with the input. (default: None)
                    multiline (bool): If True, the text is presented as a multi line input. (default: False)
                    lines_shown (int): The height of the displayed element if multiline is True. (default: 5)
                    change_delay (int): Minimum time between triggering two calls to the <i>on_change</i> callback.<br/>The default value is defined at the application configuration level by the <strong>change_delay</strong> configuration option. if None, the delay is set to 300 ms. (default: <i>App config</i>)
                    on_action (Callback): Name of a function that is triggered when a specific key is pressed.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (str): the identifier of the input.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>
        This dictionary has the following keys:
        <ul>
        <li>args (list):
        <ul><li>key name</li><li>variable name</li><li>current value</li></ul>
        </li>
        </ul>
        </li>
        </ul>
                    action_keys (str): Semicolon (';')-separated list of supported key names.<br/>Authorized values are Enter, Escape, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12. (default: "Enter")
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class number(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        value=...,
        label=...,
        change_delay=...,
        on_action=...,
        action_keys=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    value (dynamic(any)): The numerical value represented by this control.
                    label (str): The label associated with the input. (default: None)
                    change_delay (int): Minimum time between triggering two calls to the <i>on_change</i> callback.<br/>The default value is defined at the application configuration level by the <strong>change_delay</strong> configuration option. if None, the delay is set to 300 ms. (default: <i>App config</i>)
                    on_action (Callback): Name of a function that is triggered when a specific key is pressed.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (str): the identifier of the input.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>
        This dictionary has the following keys:
        <ul>
        <li>args (list):
        <ul><li>key name</li><li>variable name</li><li>current value</li></ul>
        </li>
        </ul>
        </li>
        </ul>
                    action_keys (str): Semicolon (';')-separated list of supported key names.<br/>Authorized values are Enter, Escape, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12. (default: "Enter")
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class slider(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        value=...,
        min=...,
        max=...,
        text_anchor=...,
        labels=...,
        continuous=...,
        change_delay=...,
        width=...,
        height=...,
        orientation=...,
        lov=...,
        adapter=...,
        type=...,
        value_by_id=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    value (dynamic(int|float|str)): The value that is set for this slider.<br/>It would be a <i>lov</i> label if it is used.
                    min (int|float): The minimum value.<br/>This is ignored when <i>lov</i> is defined. (default: 0)
                    max (int|float): The maximum value.<br/>This is ignored when <i>lov</i> is defined. (default: 100)
                    text_anchor (str): When the <i>lov</i> property is used, this property indicates the location of the label.<br/>Possible values are:
        <ul>
        <li>"bottom"</li>
        <li>"top"</li>
        <li>"left"</li>
        <li>"right"</li>
        <li>"none" (no label is displayed)</li>
        </ul> (default: "bottom")
                    labels (bool|dict): The labels for specific points of the slider.<br/>If set to True, this slider uses the labels of the <i>lov</i> if there are any.<br/>If set to a dictionary, the slider uses the dictionary keys as a <i>lov</i> key or index, and the associated value as the label.
                    continuous (bool): If set to False, the control emits an on_change notification only when the mouse button is released, otherwise notifications are emitted during the cursor movements.<br/>If <i>lov</i> is defined, the default value is False. (default: True)
                    change_delay (int): Minimum time between triggering two <i>on_change</i> calls.<br/>The default value is defined at the application configuration level by the <strong>change_delay</strong> configuration option. if None or 0, there's no delay. (default: <i>App config</i>)
                    width (str): The width, in CSS units, of this element. (default: "300px")
                    height (str): The height, in CSS units, of this element.<br/>It defaults to the <i>width</i> value when using the vertical orientation.
                    orientation (str): The orientation of this slider.<br/>Valid values are "horizontal" or "vertical". (default: "horizontal")
                    lov (dict[str, any]): The list of values. See the <a href="../../binding/#list-of-values">section on List of Values</a> for details.
                    adapter (Function): The function that transforms an element of <i>lov</i> into a <i>tuple(id:str, label:str|Icon)</i>. (default: `lambda x: str(x)`)
                    type (str): Must be specified if <i>lov</i> contains a non-specific type of data (ex: dict).<br/><i>value</i> must be of that type, <i>lov</i> must be an iterable on this type, and the adapter function will receive an object of this type. (default: <i>Type of first lov element</i>)
                    value_by_id (bool): If False, the selection value (in <i>value</i>) is the selected element in <i>lov</i>. If set to True, then <i>value</i> is set to the id of the selected element in <i>lov</i>. (default: False)
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class toggle(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        value=...,
        theme=...,
        allow_unselect=...,
        lov=...,
        adapter=...,
        type=...,
        value_by_id=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:

                    theme (bool): If set, this toggle control acts as a way to set the application Theme (dark or light). (default: False)
                    allow_unselect (bool): If set, this allows de-selection and the value is set to unselected_value. (default: False)
                    lov (dict[str, any]): The list of values. See the <a href="../../binding/#list-of-values">section on List of Values</a> for details.
                    adapter (Function): The function that transforms an element of <i>lov</i> into a <i>tuple(id:str, label:str|Icon)</i>. (default: `lambda x: str(x)`)
                    type (str): Must be specified if <i>lov</i> contains a non-specific type of data (ex: dict).<br/><i>value</i> must be of that type, <i>lov</i> must be an iterable on this type, and the adapter function will receive an object of this type. (default: <i>Type of first lov element</i>)
                    value_by_id (bool): If False, the selection value (in <i>value</i>) is the selected element in <i>lov</i>. If set to True, then <i>value</i> is set to the id of the selected element in <i>lov</i>. (default: False)
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class date(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        date=...,
        with_time=...,
        format=...,
        editable=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    date (dynamic(datetime)): The date that this control represents and can modify.<br/>It is typically bound to a <code>datetime</code> object.
                    with_time (bool): Whether or not to show the time part of the date. (default: False)
                    format (str): The format to apply to the value. See below.
                    editable (dynamic(bool)): Shows the date as a formatted string if not editable. (default: True)
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class chart(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        data=...,
        type=...,
        mode=...,
        x=...,
        y=...,
        z=...,
        lon=...,
        lat=...,
        r=...,
        theta=...,
        high=...,
        low=...,
        open=...,
        close=...,
        measure=...,
        locations=...,
        values=...,
        labels=...,
        text=...,
        base=...,
        title=...,
        render=...,
        on_range_change=...,
        columns=...,
        label=...,
        name=...,
        selected=...,
        color=...,
        selected_color=...,
        marker=...,
        line=...,
        selected_marker=...,
        layout=...,
        plot_config=...,
        options=...,
        orientation=...,
        text_anchor=...,
        xaxis=...,
        yaxis=...,
        width=...,
        height=...,
        template=...,
        decimator=...,
        rebuild=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    data (dynamic(any)): The data object bound to this chart control.<br/>See the section on the <a href="#the-data-property"><i>data</i> property</a> below for details.
                    type (indexed(str)): Chart type.<br/>See the Plotly <a href="https://plotly.com/javascript/reference/">chart type</a> documentation for details. (default: scatter)
                    mode (indexed(str)): Chart mode.<br/>See the Plotly <a href="https://plotly.com/javascript/reference/scatter/#scatter-mode">chart mode</a> documentation for details. (default: lines+markers)
                    x (indexed(str)): Column name for the <i>x</i> axis.
                    y (indexed(str)): Column name for the <i>y</i> axis.
                    z (indexed(str)): Column name for the <i>z</i> axis.
                    lon (indexed(str)): Column name for the <i>longitude</i> value, for 'scattergeo' charts. See <a href="https://plotly.com/javascript/reference/scattergeo/#scattergeo-lon">Plotly Map traces</a>.
                    lat (indexed(str)): Column name for the <i>latitude</i> value, for 'scattergeo' charts. See <a href="https://plotly.com/javascript/reference/scattergeo/#scattergeo-lat">Plotly Map traces</a>.
                    r (indexed(str)): Column name for the <i>r</i> value, for 'scatterpolar' charts. See <a href="https://plotly.com/javascript/polar-chart/">Plotly Polar charts</a>.
                    theta (indexed(str)): Column name for the <i>theta</i> value, for 'scatterpolar' charts. See <a href="https://plotly.com/javascript/polar-chart/">Plotly Polar charts</a>.
                    high (indexed(str)): Column name for the <i>high</i> value, for 'candlestick' charts. See <a href="https://plotly.com/javascript/reference/candlestick/#candlestick-high">Plotly Candlestick charts</a>.
                    low (indexed(str)): Column name for the <i>low</i> value, for 'candlestick' charts. See <a href="https://plotly.com/javascript/reference/candlestick/#candlestick-low">Ploty Candlestick charts</a>.
                    open (indexed(str)): Column name for the <i>open</i> value, for 'candlestick' charts. See <a href="https://plotly.com/javascript/reference/candlestick/#candlestick-open">Plotly Candlestick charts</a>.
                    close (indexed(str)): Column name for the <i>close</i> value, for 'candlestick' charts. See <a href="https://plotly.com/javascript/reference/candlestick/#candlestick-close">Plotly Candlestick charts</a>.
                    measure (indexed(str)): Column name for the <i>measure</i> value, for 'waterfall' charts. See <a href="https://plotly.com/javascript/reference/waterfall/#waterfall-measure">Plotly Waterfall charts</a>.
                    locations (indexed(str)): Column name for the <i>locations</i> value. See <a href="https://plotly.com/javascript/choropleth-maps/">Plotly Choropleth maps</a>.
                    values (indexed(str)): Column name for the <i>values</i> value. See <a href="https://plotly.com/javascript/reference/pie/#pie-values">Plotly Pie charts</a> or <a href="https://plotly.com/javascript/reference/funnelarea/#funnelarea-values">Plotly Funnel Area charts</a>.
                    labels (indexed(str)): Column name for the <i>labels</i> value. See <a href="https://plotly.com/javascript/reference/pie/#pie-labels">Plotly Pie charts</a>.
                    text (indexed(str)): Column name for the text associated to the point for the indicated trace.<br/>This is meaningful only when <i>mode</i> has the <i>text</i> option.
                    base (indexed(str)): Column name for the <i>base</i> value. Used in bar charts only.<br/>See the Plotly <a href="https://plotly.com/javascript/reference/bar/#bar-base">bar chart base</a> documentation for details."
                    title (str): The title of this chart control.
                    render (dynamic(bool)): If True, this chart is visible on the page. (default: True)
                    on_range_change (Callback): The callback function that is invoked when the visible part of the x axis changes.<br/>The function receives four parameters:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (optional[str]): the identifier of the chart control.</li>
        <li>action (optional[str]): the name of the action that provoked the change.</li>
        <li>payload (dict[str, any]): the full details on this callback's invocation, as emitted by <a href="https://plotly.com/javascript/plotlyjs-events/#update-data">Plotly</a>.</li>
        </ul>
                    columns (str|list[str]|dict[str, dict[str, str]]): The list of column names
        <ul>
        <li>str: ;-separated list of column names</li>
        <li>list[str]: list of names</li>
        <li>dict: {"column_name": {format: "format", index: 1}} if index is specified, it represents the display order of the columns.
        If not, the list order defines the index</li>
        </ul> (default: _All columns_)
                    label (indexed(str)): The label for the indicated trace.<br/>This is used when the mouse hovers over a trace.
                    name (indexed(str)): The name of the indicated trace.
                    selected (indexed(dynamic(list[int]|str))): The list of the selected point indices  .
                    color (indexed(str)): The color of the indicated trace (or a column name for scattered).
                    selected_color (indexed(str)): The color of the selected points for the indicated trace.
                    marker (indexed(dict[str, any])): The type of markers used for the indicated trace.<br/>See <a href="https://plotly.com/javascript/reference/scatter/#scatter-marker">marker</a> for details.<br/>Color, opacity, size and symbol can be column name.
                    line (indexed(str|dict[str, any])): The configuration of the line used for the indicated trace.<br/>See <a href="https://plotly.com/javascript/reference/scatter/#scatter-line">line</a> for details.<br/>If the value is a string, it must be a dash type or pattern (see <a href="https://plotly.com/python/reference/scatter/#scatter-line-dash">dash style of lines</a> for details).
                    selected_marker (indexed(dict[str, any])): The type of markers used for selected points in the indicated trace.<br/>See <a href="https://plotly.com/javascript/reference/scatter/#scatter-selected-marker">selected marker for details.
                    layout (dynamic(dict[str, any])): The <i>plotly.js</i> compatible <a href="https://plotly.com/javascript/reference/layout/">layout object</a>.
                    plot_config (dict[str, any]): The <i>plotly.js</i> compatible <a href="https://plotly.com/javascript/configuration-options/"> configuration options object</a>.
                    options (indexed(dict[str, any])): The <i>plotly.js</i> compatible <a href="https://plotly.com/javascript/reference/">data object where dynamic data will be overridden.</a>.
                    orientation (indexed(str)): The orientation of the indicated trace.
                    text_anchor (indexed(str)): Position of the text relative to the point.<br/>Valid values are: <i>top</i>, <i>bottom</i>, <i>left</i>, and <i>right</i>.
                    xaxis (indexed(str)): The <i>x</i> axis identifier for the indicated trace.
                    yaxis (indexed(str)): The <i>y</i> axis identifier for the indicated trace.
                    width (str|int|float): The width, in CSS units, of this element. (default: 100%)
                    height (str|int|float): The height, in CSS units, of this element.
                    template (dict): The Plotly layout <a href="https://plotly.com/javascript/layout-template/">template</a>.
                    decimator (indexed(taipy.gui.data.Decimator)): A decimator instance for the indicated trace that will reduce the size of the data being sent back and forth.<br>If defined as indexed, it will impact only the indicated trace; if not, it will apply only the the first trace.
                    rebuild (dynamic(bool)): Allows dynamic config refresh if set to True. (default: False)
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class file_download(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        content=...,
        label=...,
        on_action=...,
        auto=...,
        render=...,
        bypass_preview=...,
        name=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    content (dynamic(url|path|file|ReadableBuffer)): The content of the file.<br/>If a buffer is provided (string, array of bytes...), and in order to prevent the bandwidth to be consumed too much, the way the data is transferred depends on the the <i>data_url_max_size</i> parameter of the application configuration (which is set to 50kB by default):
        <ul>
        <li>If the size of the buffer is smaller than this setting, then the raw content is generated as a data URL, encoded using base64 (i.e. <code>"data:&lt;mimetype&gt;;base64,&lt;data&gt;"</code>).</li>
        <li>If the size of the buffer is greater than this setting, then it is transferred through a temporary file.</li>
        </ul>
                    label (dynamic(str)): The label of the button.
                    on_action (Callback): The name of a function that is triggered when the download is initiated.<br/>All the parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (optional[str]): the identifier of the button.</li>
        <li>action (optional[str]): the name of the action that provoked the change.</li>
        </ul>
                    auto (bool): If True, the download starts as soon as the page is loaded. (default: False)
                    render (dynamic(bool)): If True, the control is displayed.<br/>If False, the control is not displayed. (default: True)
                    bypass_preview (bool): If False, allows the browser to try to show the content in a different tab.<br/>The file download is always performed. (default: True)
                    name (str): A name proposition for the file to save, that the user can change.
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class file_selector(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        content=...,
        label=...,
        on_action=...,
        multiple=...,
        extensions=...,
        drop_message=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    content (dynamic(str)): The path or the list of paths of the uploaded files.
                    label (str): The label of the button.
                    on_action (Callback): The name of the function that will be triggered.<br/>All the parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (optional[str]): the identifier of the button.</li>
        <li>action (optional[str]): the name of the action that provoked the change.</li>
        </ul>
                    multiple (bool): If set to True, multiple files can be uploaded. (default: False)
                    extensions (str): The list of file extensions that can be uploaded. (default: ".csv,.xlsx")
                    drop_message (str): The message that is displayed when the user drags a file above the button. (default: "Drop here to Upload")
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class image(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        content=...,
        label=...,
        on_action=...,
        width=...,
        height=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    content (dynamic(url|path|file|ReadableBuffer)): The image source.<br/>If a buffer is provided (string, array of bytes...), and in order to prevent the bandwidth to be consumed too much, the way the image data is transferred depends on the the <i>data_url_max_size</i> parameter of the application configuration (which is set to 50kB by default):
        <ul>
        <li>If the size of the buffer is smaller than this setting, then the raw content is generated as a
          data URL, encoded using base64 (i.e. <code>"data:&lt;mimetype&gt;;base64,&lt;data&gt;"</code>).</li>
        <li>If the size of the buffer is greater than this setting, then it is transferred through a temporary
          file.</li>
        </ul>
                    label (dynamic(str)): The label for this image.
                    on_action (str): The name of a function that is triggered when the user clicks on the image.<br/>All the parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (optional[str]): the identifier of the button.</li>
        <li>action (optional[str]): the name of the action that provoked the change.</li>
        </ul>
                    width (str|int|float): The width, in CSS units, of this element. (default: "300px")
                    height (str|int|float): The height, in CSS units, of this element.
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class indicator(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        display=...,
        value=...,
        min=...,
        max=...,
        format=...,
        orientation=...,
        width=...,
        height=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
        Arguments:
            display (dynamic(any)): The label to be displayed.<br/>This can be formatted if it is a numerical value.
            value (dynamic(int,float)): The location of the label on the [<i>min</i>, <i>max</i>] range. (default: <i>min</i>)
            min (int|float): The minimum value of the range. (default: 0)
            max (int|float): The maximum value of the range. (default: 100)
            format (str): The format to use when displaying the value.<br/>This uses the <code>printf</code> syntax.
            orientation (str): The orientation of this slider. (default: "horizontal")
            width (str): The width, in CSS units, of the indicator (used when orientation is horizontal). (default: None)
            height (str): The height, in CSS units, of the indicator (used when orientation is vartical). (default: None)
            id (str): The identifier that will be assigned to the rendered HTML component.
            properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
            class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
            hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class menu(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(self, lov=..., adapter=..., type=..., label=..., width=..., on_action=..., active=...) -> None:
        """
                Arguments:
                    lov (dynamic(str|list[str|Icon|any])): The list of menu option values.
                    adapter (Function): The function that transforms an element of <i>lov</i> into a <i>tuple(id:str, label:str|Icon)</i>. (default: `"lambda x: str(x)"`)
                    type (str): Must be specified if <i>lov</i> contains a non specific type of data (ex: dict).<br/><i>value</i> must be of that type, <i>lov</i> must be an iterable on this type, and the adapter function will receive an object of this type. (default: <i>Type of the first lov element</i>)
                    label (str): The title of the menu.
                    width (str): The width, in CSS units, of the menu when unfolded.<br/>Note that when running on a mobile device, the property <i>width[active]</i> is used instead. (default: "15vw")
                    on_action (Callback): The name of the function that is triggered when a menu option is selected.<br/><br/>All the parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (str): the identifier of the button.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>
        This dictionary has the following keys:
        <ul>
        <li>args: List where the first element contains the id of the selected option.</li>
        </ul>
        </li>
        </ul>
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
        """
        ...

class navbar(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(self, lov=..., active=..., id=..., properties=..., class_name=..., hover_text=...) -> None:
        """
        Arguments:
            lov (dict[str, any]): The list of pages. The keys should be page id and start with "/", the values are labels. See the <a href="../../binding/#list-of-values">section on List of Values</a> for details.
            active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
            id (str): The identifier that will be assigned to the rendered HTML component.
            properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
            class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
            hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class selector(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        filter=...,
        multiple=...,
        width=...,
        height=...,
        dropdown=...,
        label=...,
        value=...,
        lov=...,
        adapter=...,
        type=...,
        value_by_id=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    filter (bool): If True, this control is combined with a filter input area. (default: False)
                    multiple (bool): If True, the user can select multiple items. (default: False)
                    width (str|int): The width, in CSS units, of this element. (default: "360px")
                    height (str|int): The height, in CSS units, of this element.
                    dropdown (bool): If True, the list of items is shown in a dropdown menu.<br/><br/>You cannot use the filter in that situation. (default: False)
                    label (str): The label associated with the selector when in dropdown mode. (default: None)
                    value (dynamic(any)): Bound to the selection value.
                    lov (dict[str, any]): The list of values. See the <a href="../../binding/#list-of-values">section on List of Values</a> for details.
                    adapter (Function): The function that transforms an element of <i>lov</i> into a <i>tuple(id:str, label:str|Icon)</i>. (default: `lambda x: str(x)`)
                    type (str): Must be specified if <i>lov</i> contains a non-specific type of data (ex: dict).<br/><i>value</i> must be of that type, <i>lov</i> must be an iterable on this type, and the adapter function will receive an object of this type. (default: <i>Type of first lov element</i>)
                    value_by_id (bool): If False, the selection value (in <i>value</i>) is the selected element in <i>lov</i>. If set to True, then <i>value</i> is set to the id of the selected element in <i>lov</i>. (default: False)
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class status(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(self, value=..., without_close=..., id=..., properties=..., class_name=..., hover_text=...) -> None:
        """
        Arguments:
            value (tuple|dict|list[dict]|list[tuple]): The different status items to represent. See below.
            without_close (bool): If True, the user cannot remove the status items from the list. (default: False)
            id (str): The identifier that will be assigned to the rendered HTML component.
            properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
            class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
            hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class table(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        data=...,
        page_size=...,
        allow_all_rows=...,
        show_all=...,
        auto_loading=...,
        selected=...,
        page_size_options=...,
        columns=...,
        date_format=...,
        number_format=...,
        style=...,
        tooltip=...,
        width=...,
        height=...,
        filter=...,
        nan_value=...,
        editable=...,
        on_edit=...,
        on_delete=...,
        on_add=...,
        on_action=...,
        size=...,
        rebuild=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    data (dynamic(any)): The data to be represented in this table.
                    page_size (int): For a paginated table, the number of visible rows. (default: 100)
                    allow_all_rows (bool): For a paginated table, adds an option to show all the rows. (default: False)
                    show_all (bool): For a paginated table, show all the rows. (default: False)
                    auto_loading (bool): If True, the data will be loaded on demand. (default: False)
                    selected (list[int]|str): The list of the indices of the rows to be displayed as selected.
                    page_size_options (list[int]|str): The list of available page sizes that users can choose from. (default: [50, 100, 500])
                    columns (str|list[str]|dict[str, dict[str, str|int]]): The list of the column names to display.
        <ul>
        <li>str: Semicolon (';')-separated list of column names.</li>
        <li>list[str]: The list of column names.</li>
        <li>dict: A dictionary with entries matching: {"col name": {format: "format", index: 1}}.<br/>
        if <i>index</i> is specified, it represents the display order of the columns.
        If <i>index</i> is not specified, the list order defines the index.<br/>
        If <i>format</i> is specified, it is used for numbers or dates.</li>
        </ul> (default: <i>shows all columns when empty</i>)
                    date_format (str): The date format used for all date columns when the format is not specifically defined. (default: "MM/dd/yyyy")
                    number_format (str): The number format used for all number columns when the format is not specifically defined.
                    style (str): Allows the styling of table lines.<br/>See <a href="#dynamic-styling">below</a> for details.
                    tooltip (str): The name of the function that must return a tooltip text for a cell.<br/>See <a href="#cell%20tooltip">below</a> for details.
                    width (str): The width, in CSS units, of this table control. (default: "100%")
                    height (str): The height, in CSS units, of this table control. (default: "80vh")
                    filter (bool): Indicates, if True, that all columns can be filtered. (default: False)
                    nan_value (str): The replacement text for NaN (not-a-number) values. (default: "")
                    editable (dynamic(bool)): Indicates, if True, that all columns can be edited. (default: True)
                    on_edit (Callback): The name of a function that is triggered when a cell edition is validated.<br/>All parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the name of the tabular data variable.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>
        This dictionary has the following keys:
        <ul>
        <li>index (int): the row index.</li>
        <li>col (str): the column name.</li>
        <li>value (any): the new cell value cast to the type of the column.</li>
        <li>user_value (str): the new cell value, as it was provided by the user.</li>
        </ul>
        </li>
        </ul><br/>If this property is not set, the user cannot edit cells.
                    on_delete (str): The name of a function that is triggered when a row is deleted.<br/>All parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the name of the tabular data variable.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>
        This dictionary has the following keys:
        <ul>
        <li>index (int): the row index.</li>
        </ul>
        </li>
        </ul><br/>If this property is not set, the user cannot delete rows.
                    on_add (str): The name of a function that is triggered when the user requests a row to be added.<br/>All parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the name of the tabular data variable.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>This dictionary has the following keys:
        <ul>
        <li>index (int): the row index.</li>
        </ul>
        </li>
        </ul><br/>If this property is not set, the user cannot add rows.
                    on_action (str): The name of a function that is triggered when the user selects a row.<br/>All parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the name of the tabular data variable.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>This dictionary has the following keys:
        <ul>
        <li>index (int): the row index.</li>
        <li>col (str): the column name.</li></ul></li></ul>.
                    size (str): The size of the rows.<br/>Valid values are "small" and "medium". (default: "small")
                    rebuild (dynamic(bool)): If set to True, this allows to dynamically refresh the  columns. (default: False)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class dialog(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        open=...,
        on_action=...,
        close_label=...,
        labels=...,
        width=...,
        height=...,
        partial=...,
        page=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    open (bool): If True, the dialog is visible. If False, it is hidden. (default: False)
                    on_action (Callback): Name of a function triggered when a button is pressed.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (str): the identifier of the dialog.</li>
        <li>action (str): the name of the action that provoked the change.</li>
        <li>payload (dict): the details on this callback's invocation.<br/>This dictionary has the following keys:
        <ul>
        <li>args: a list where the first element contains the index of the selected label.</li>
        </ul>
        </li>
        </ul>
                    close_label (str): The tooltip of the top-right close icon button. In the <strong>on_action</strong> function, args will hold -1. (default: "Close")
                    labels ( str|list[str]): A list of labels to show in a row of buttons at the bottom of the dialog. The index of the button in the list is reported as args in the <strong>on_action</strong> function (-1 for the close icon).
                    width (str|int|float): The width, in CSS units, of this dialog.<br/>(CSS property)
                    height (str|int|float): The height, in CSS units, of this dialog.<br/>(CSS property)
                    partial (Partial): A Partial object that holds the content of the block.<br/>This should not be defined if <i>page</i> is set.
                    page (str): The page name to show as the content of the block.<br/>This should not be defined if <i>partial</i> is set.
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class tree(ControlElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        expanded=...,
        multiple=...,
        select_leafs_only=...,
        row_height=...,
        filter=...,
        width=...,
        height=...,
        dropdown=...,
        label=...,
        value=...,
        lov=...,
        adapter=...,
        type=...,
        value_by_id=...,
        on_change=...,
        propagate=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    expanded (dynamic(bool|str[])): If Boolean and False, only one node can be expanded at one given level. Otherwise this should be set to an array of the node identifiers that need to be expanded. (default: True)
                    multiple (bool): If True, the user can select multiple items by holding the <code>Ctrl</code> key while clicking on items. (default: False)
                    select_leafs_only (bool): If True, the user can only select leaf nodes. (default: False)
                    row_height (str): The height, in CSS units, of each row.
                    filter (bool): If True, this control is combined with a filter input area. (default: False)
                    width (str|int): The width, in CSS units, of this element. (default: "360px")
                    height (str|int): The height, in CSS units, of this element.
                    dropdown (bool): If True, the list of items is shown in a dropdown menu.<br/><br/>You cannot use the filter in that situation. (default: False)
                    label (str): The label associated with the selector when in dropdown mode. (default: None)
                    value (dynamic(any)): Bound to the selection value.
                    lov (dict[str, any]): The list of values. See the <a href="../../binding/#list-of-values">section on List of Values</a> for details.
                    adapter (Function): The function that transforms an element of <i>lov</i> into a <i>tuple(id:str, label:str|Icon)</i>. (default: `lambda x: str(x)`)
                    type (str): Must be specified if <i>lov</i> contains a non-specific type of data (ex: dict).<br/><i>value</i> must be of that type, <i>lov</i> must be an iterable on this type, and the adapter function will receive an object of this type. (default: <i>Type of first lov element</i>)
                    value_by_id (bool): If False, the selection value (in <i>value</i>) is the selected element in <i>lov</i>. If set to True, then <i>value</i> is set to the id of the selected element in <i>lov</i>. (default: False)
                    on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
                    propagate (bool): Allows the control's main value to be automatically propagated.<br/>The default value is defined at the application configuration level.<br/>If True, any change to the control's value is immediately reflected in the bound application variable. (default: <i>App config</i>)
                    active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)
                    id (str): The identifier that will be assigned to the rendered HTML component.
                    properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.
                    class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.
                    hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class part(BlockElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self, render=..., class_name=..., page=..., height=..., partial=..., id=..., properties=..., hover_text=...
    ) -> None:
        """
        Arguments:
            render (dynamic(bool)): If True, this part is visible on the page.<br/>If False, the part is hidden and its content is not displayed. (default: True)        class_name (dynamic(str)): A list of CSS class names, separated by white spaces, that will be associated with the generated HTML Element.<br/>These class names are added to the default <code>taipy-part</code>.         page (dynamic(str)): The page to show as the content of the block (page name if defined or an URL in an <i>iframe</i>).<br/>This should not be defined if <i>partial</i> is set.         height (dynamic(str)): The height, in CSS units, of this block.         partial (Partial): A Partial object that holds the content of the block.<br/>This should not be defined if <i>page</i> is set.         id (str): The identifier that will be assigned to the rendered HTML component.         properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.         hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class expandable(BlockElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        value=...,
        expanded=...,
        partial=...,
        page=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
        on_change=...,
    ) -> None:
        """
                Arguments:
                    value (dynamic(str)): Title of this block element.         expanded (dynamic(bool)): If True, the block is expanded, and the content is displayed.<br/>If False, the block is collapsed and its content is hidden. (default: True)        partial (Partial): A Partial object that holds the content of the block.<br/>This should not be defined if <i>page</i> is set.         page (str): The page name to show as the content of the block.<br/>This should not be defined if <i>partial</i> is set.         id (str): The identifier that will be assigned to the rendered HTML component.         properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.         class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.         hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.         on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>
        """
        ...

class layout(BlockElementApi):
    _ELEMENT_NAME: str
    def __init__(self, columns=..., gap=..., id=..., properties=..., class_name=..., hover_text=...) -> None:
        """
                Arguments:
                    columns (str): The list of weights for each column.<br/>For example, `"1 2"` creates a 2 column grid:
        <ul>
        <li>1fr</li>
        <li>2fr</li>
        </ul><br/>The creation of multiple same size columns can be simplified by using the multiply sign eg. "5*1" is equivalent to "1 1 1 1 1". (default: "1 1")        gap (str): The size of the gap between the columns. (default: "0.5rem")        id (str): The identifier that will be assigned to the rendered HTML component.         properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.         class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.         hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...

class pane(BlockElementApi):
    _ELEMENT_NAME: str
    def __init__(
        self,
        open=...,
        on_close=...,
        anchor=...,
        width=...,
        height=...,
        persistent=...,
        partial=...,
        page=...,
        on_change=...,
        active=...,
        id=...,
        properties=...,
        class_name=...,
        hover_text=...,
    ) -> None:
        """
                Arguments:
                    open (dynamic(bool)): If True, this pane is visible on the page.<br/>If False, the pane is hidden. (default: False)        on_close (Callback): The name of a function that is triggered when this pane is closed (if the user clicks outside of it or presses the Esc key).<br/>All parameters of that function are optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>id (optional[str]): the identifier of the button.</li>
        <li>action (optional[str]): the name of the action that provoked the change.</li>
        </ul><br/>If this property is not set, no function is called when this pane is closed.         anchor (str): Anchor side of the pane.<br/>Valid values are "left", "right", "top", or "bottom". (default: "left")        width (str): Width, in CSS units, of this pane.<br/>This is used only if <i>anchor</i> is "left" or "right". (default: "30vw")        height (str): Height, in CSS units, of this pane.<br/>This is used only if <i>anchor</i> is "top" or "bottom". (default: "30vh")        persistent (bool): If False, the pane covers the page where it appeared and disappears if the user clicks in the page.<br/>If True, the pane appears next to the page. Note that the parent section of the pane must have the <i>flex</i> display mode set. See below for an example using the <code>persistent</code> property. (default: False)        partial (Partial): A Partial object that holds the content of the block.<br/>This should not be defined if <i>page</i> is set.         page (str): The page name to show as the content of the block.<br/>This should not be defined if <i>partial</i> is set.         on_change (Callback): The name of a function that is triggered when the value is updated.<br/>The parameters of that function are all optional:
        <ul>
        <li>state (<code>State^</code>): the state instance.</li>
        <li>var_name (str): the variable name.</li>
        <li>value (any): the new value.</li>
        </ul>         active (dynamic(bool)): Indicates if this component is active.<br/>An inactive component allows no user interaction. (default: True)        id (str): The identifier that will be assigned to the rendered HTML component.         properties (dict[str, any]): Bound to a dictionary that contains additional properties for this element.         class_name (dynamic(str)): The list of CSS class names that will be associated with the generated HTML Element.<br/>These class names will be added to the default <code>taipy-&lt;element_type&gt;</code>.         hover_text (dynamic(str)): The information that is displayed when the user hovers over this element.
        """
        ...
