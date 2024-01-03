# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import threading
import typing as t

from ._warnings import _warn
from .gui import Gui
from .state import State


def download(
    state: State, content: t.Any, name: t.Optional[str] = "", on_action: t.Optional[t.Union[str, t.Callable]] = ""
):
    """Download content to the client.

    Arguments:
        state (State^): The current user state as received in any callback.
        content: File path or file content. See below.
        name: File name for the content on the client browser (defaults to content name).
        on_action: Callback function (or callback name) to call when the download ends. See below.

    ## Notes:

    - *content*: this parameter can hold several values depending on your use case:
        - a string: the value must be an existing path name to the file that gets downloaded or
          the URL to the resource you want to download.
        - a buffer (such as a `bytes` object): if the size of the buffer is smaller than
           the [*data_url_max_size*](../gui/configuration.md#p-data_url_max_size) configuration
           setting, then the [`python-magic`](https://pypi.org/project/python-magic/) package is
           used to determine the [MIME type](https://en.wikipedia.org/wiki/Media_type) of the
           buffer content, and the download is performed using a generated "data:" URL with
           the relevant type, and a base64-encoded version of the buffer content.<br/>
           If the buffer is too large, its content is transferred after saving it in a temporary
           server file.
      - *on_action*: this callback is triggered when the transfer of the content is achieved.</br>
           In this function, you can perform any clean-up operation that could be required after
           the download is completed.<br/>
           This callback can use three optional parameters:
           - *state*: the `State^` instance of the caller.
           - *id* (optional): a string representing the identifier of the caller. If this function
             is called directly, this will always be "Gui.download". Some controls may also trigger
             download actions, and then *id* would reflect the identifier of those controls.
           - *payload* (optional): an optional payload from the caller.<br/>
             This is a dictionary with the following keys:
              - *action*: the name of the callback;
              - *args*: an array of two strings. The first element reflects the *name* parameter,
                and the second element reflects the server-side URL where the file is located.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._download(content, name, on_action)
    else:
        _warn("'download()' must be called in the context of a callback.")


def notify(
    state: State,
    notification_type: str = "I",
    message: str = "",
    system_notification: t.Optional[bool] = None,
    duration: t.Optional[int] = None,
):
    """Send a notification to the user interface.

    Arguments:
        state (State^): The current user state as received in any callback.
        notification_type: The notification type. This can be one of "success", "info",
            "warning", or "error".<br/>
            To remove the last notification, set this parameter to the empty string.
        message: The text message to display.
        system_notification: If True, the system will also show the notification.<br/>
            If not specified or set to None, this parameter will use the value of
            *configuration[system_notification]*.
        duration: The time, in milliseconds, during which the notification is shown.
            If not specified or set to None, this parameter will use the value of
            *configuration[notification_duration]*.

    Note that you can also call this function with *notification_type* set to the first letter
    or the alert type (i.e. setting *notification_type* to "i" is equivalent to setting it to
    "info").

    If *system_notification* is set to True, then the browser requests the system
    to display a notification as well. They usually appear in small windows that
    fly out of the system tray.<br/>
    The first time your browser is requested to show such a system notification for
    Taipy applications, you may be prompted to authorize the browser to do so. Please
    refer to your browser documentation for details on how to allow or prevent this
    feature.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._notify(notification_type, message, system_notification, duration)
    else:
        _warn("'notify()' must be called in the context of a callback.")


def hold_control(
    state: State,
    callback: t.Optional[t.Union[str, t.Callable]] = None,
    message: t.Optional[str] = "Work in Progress...",
):
    """Hold the User Interface actions.

    When the User Interface is held, users cannot interact with visual elements.<br/>
    The application must call `resume_control()^` so that users can interact again
    with the visual elements.

    You can set a callback function (or the name of a function) in the *callback* parameter. Then,
    a "Cancel" button will be displayed so the user can cancel whatever is happening in the
    application. When pressed, the callback is invoked.

    Arguments:
        state (State^): The current user state received in any callback.
        callback (Optional[Union[str, Callable]]): The function to be called if the user
            chooses to cancel.<br/>
            If empty or None, no cancel action is provided to the user.<br/>
            The signature of this function is:
            - state (State^): The user state;
            - id (str): the id of the button that triggered the callback. That will always be
              "UIBlocker" since it is created and managed internally;
        message: The message to show. The default value is the string "Work in Progress...".
    """
    if state and isinstance(state._gui, Gui):
        state._gui._hold_actions(callback, message)
    else:
        _warn("'hold_actions()' must be called in the context of a callback.")


def resume_control(state: State):
    """Resume the User Interface actions.

    This function must be called after `hold_control()^` was invoked, when interaction
    must be allowed again for the user.

    Arguments:
        state (State^): The current user state as received in any callback.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._resume_actions()
    else:
        _warn("'resume_actions()' must be called in the context of a callback.")


def navigate(
    state: State,
    to: t.Optional[str] = "",
    params: t.Optional[t.Dict[str, str]] = None,
    tab: t.Optional[str] = None,
    force: t.Optional[bool] = False,
):
    """Navigate to a page.

    Arguments:
        state (State^): The current user state as received in any callback.
        to: The name of the page to navigate to. This can be a page identifier (as created by
            `Gui.add_page()^` with no leading '/') or an URL.<br/>
            If omitted, the application navigates to the root page.
        params: A dictionary of query parameters.
        tab: When navigating to a page that is not a known page, the page is opened in a tab identified by
            *tab* (as in [window.open](https://developer.mozilla.org/en-US/docs/Web/API/Window/open)).<br/>
            The default value creates a new tab for the page (which is equivalent to setting *tab* to "_blank").
        force: When navigating to a known page, the content is refreshed even it the page is already shown.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._navigate(to, params, tab, force)
    else:
        _warn("'navigate()' must be called in the context of a callback.")


def get_user_content_url(
    state: State, path: t.Optional[str] = None, params: t.Optional[t.Dict[str, str]] = None
) -> t.Optional[str]:
    """Get a user content URL.

    This function can be used if you need to deliver dynamic content to your page: you can create
    a path at run-time that, when queried, will deliver some user-defined content defined in the
    *on_user_content* callback (see the description of the `Gui^` class for more information).

    Arguments:
        state (State^): The current user state as received in any callback.
        path: An optional additional path to the URL.
        params: An optional dictionary sent to the *on_user_content* callback.<br/>
            These arguments are added as query parameters to the generated URL and converted into
            strings.

    Returns:
        An URL that, when queried, triggers the *on_user_content* callback.
    """
    if state and isinstance(state._gui, Gui):
        return state._gui._get_user_content_url(path, params)
    _warn("'get_user_content_url()' must be called in the context of a callback.")
    return None


def get_state_id(state: State) -> t.Optional[str]:
    """Get the identifier of a state.

    The state identifier is a string generated by Taipy GUI for a given `State^` that is used
    to serialize callbacks.
    See the
    [User Manual section on Long Running Callbacks](../gui/callbacks.md#long-running-callbacks)
    for details on when and how this function can be used.

    Arguments:
        state (State^): The current user state as received in any callback.

    Returns:
        A string that uniquely identifies the state.<br/>
        If None, then **state** was not handled by a `Gui^` instance.
    """
    if state and isinstance(state._gui, Gui):
        return state._gui._get_client_id()
    return None


def get_module_context(state: State) -> t.Optional[str]:
    """Get the name of the module currently in used when using page scopes

    Arguments:
        state (State^): The current user state as received in any callback.

    Returns:
        The name of the current module
    """
    if state and isinstance(state._gui, Gui):
        return state._gui._get_locals_context()
    return None


def get_context_id(state: State) -> t.Any:
    _warn("'get_context_id()' was deprecated in Taipy GUI 2.0. Use 'get_state_id()' instead.")
    return get_state_id(state)


def get_module_name_from_state(state: State) -> t.Optional[str]:
    """Get the module name that triggered a callback.

    Pages can be defined in different modules yet refer to callback functions declared elsewhere
    (typically, the application's main module).

    This function returns the name of the module where the page that holds the control that
    triggered the callback was declared.  This lets applications implement different behaviors
    depending on what page is involved.

    This function must be called only in the body of a callback function.

    Arguments:
        state (State^): The `State^` instance, as received in any callback.

    Returns:
        The name of the module that holds the definition of the page containing the control
            that triggered the callback that was provided the *state* object.
    """
    if state and isinstance(state._gui, Gui):
        return state._gui._get_locals_context()
    return None


def invoke_callback(
    gui: Gui,
    state_id: str,
    callback: t.Callable,
    args: t.Union[t.Tuple, t.List],
    module_context: t.Optional[str] = None,
) -> t.Any:
    """Invoke a user callback for a given state.

    See the
    [User Manual section on Long Running Callbacks in a Thread](../gui/callbacks.md#long-running-callbacks-in-a-thread)
    for details on when and how this function can be used.

    Arguments:
        gui (Gui^): The current Gui instance.
        state_id: The identifier of the state to use, as returned by `get_state_id()^`.
        callback (Callable[[State^, ...], None]): The user-defined function that is invoked.<br/>
            The first parameter of this function **must** be a `State^`.
        args (Union[Tuple, List]): The remaining arguments, as a List or a Tuple.
        module_context (Optional[str]): the name of the module that will be used.
    """
    if isinstance(gui, Gui):
        return gui._call_user_callback(state_id, callback, list(args), module_context)
    _warn("'invoke_callback()' must be called with a valid Gui instance.")


def broadcast_callback(
    gui: Gui,
    callback: t.Callable,
    args: t.Optional[t.Union[t.Tuple, t.List]] = None,
    module_context: t.Optional[str] = None,
) -> t.Any:
    """Invoke a callback for every client.

    This callback gets invoked for every client connected to the application with the appropriate
    `State^` instance. You can then perform client-specific tasks, such as updating the state
    variable reflected in the user interface.

    Arguments:
        gui (Gui^): The current Gui instance.
        callback: The user-defined function to be invoked.<br/>
            The first parameter of this function must be a `State^` object representing the
            client for which it is invoked.<br/>
            The other parameters should reflect the ones provided in the *args* collection.
        args: The parameters to send to *callback*, if any.
    """
    if isinstance(gui, Gui):
        return gui._call_broadcast_callback(callback, list(args) if args else [], module_context)
    _warn("'broadcast_callback()' must be called with a valid Gui instance.")


def invoke_state_callback(gui: Gui, state_id: str, callback: t.Callable, args: t.Union[t.Tuple, t.List]) -> t.Any:
    _warn("'invoke_state_callback()' was deprecated in Taipy GUI 2.0. Use 'invoke_callback()' instead.")
    return invoke_callback(gui, state_id, callback, args)


def invoke_long_callback(
    state: State,
    user_function: t.Callable,
    user_function_args: t.Union[t.Tuple, t.List] = None,
    user_status_function: t.Optional[t.Callable] = None,
    user_status_function_args: t.Union[t.Tuple, t.List] = None,
    period=0,
):
    """Invoke a long running user callback.

    Long-running callbacks are run in a separate thread to not block the application itself.

    This function expects to be provided a function to run in the background (in *user_function*).<br/>
    It can also be specified a *status function* that is called when the operation performed by
    *user_function* is finished (successfully or not), or periodically (using the *period* parameter).

    See the
    [User Manual section on Long Running Callbacks](../gui/callbacks.md#long-running-callbacks)
    for details on when and how this function can be used.

    Arguments:
        state (State^): The `State^` instance, as received in any callback.
        user_function (Callable[[...], None]): The function that will be run independently of Taipy GUI. Note
            that this function must not use *state*, which is not persisted across threads.
        user_function_args (Optional[List|Tuple]): The arguments to send to *user_function*.
        user_status_function (Optional(Callable[[State^, bool, ...], None])): The optional user-defined status
            function that is invoked at the end of and possibly during the runtime of *user_function*:

            - The first parameter of this function is set to a `State^` instance.
            - The second parameter of this function is set to a bool or an int, depending on the
              conditions under which it is called:

               - If this parameter is set to a bool value, then:

                   - If True, this indicates that *user_function* has finished properly.
                        The last argument passed will be the result of the user_function call.
                   - If False, this indicates that *user_function* failed.

               - If this parameter is set to an int value, then this value indicates
                 how many periods (as lengthy as indicated in *period*) have elapsed since *user_function* was
                 started.
        user_status_function_args (Optional[List|Tuple]): The remaining arguments of the user status function.
        period (int): The interval, in milliseconds, at which *user_status_function* is called.<br/>
            The default value is 0, meaning no call to *user_status_function* will happen until *user_function*
            terminates (then the second parameter of that call will be ).</br>
            When set to a value smaller than 500, *user_status_function* is called only when *user_function*
            terminates (as if *period* was set to 0).
    """
    if not state or not isinstance(state._gui, Gui):
        _warn("'invoke_long_callback()' must be called in the context of a callback.")

    if user_status_function_args is None:
        user_status_function_args = []
    if user_function_args is None:
        user_function_args = []
        return

    if user_status_function_args is None:
        user_status_function_args = []
    if user_function_args is None:
        user_function_args = []

    state_id = get_state_id(state)
    module_context = get_module_context(state)
    if not isinstance(state_id, str) or not isinstance(module_context, str):
        return

    this_gui = state._gui

    def callback_on_exception(state: State, function_name: str, e: Exception):
        if not this_gui._call_on_exception(function_name, e):
            _warn(f"invoke_long_callback(): Exception raised in function {function_name}()", e)

    def callback_on_status(
        status: t.Union[int, bool],
        e: t.Optional[Exception] = None,
        function_name: t.Optional[str] = None,
        function_result: t.Optional[t.Any] = None,
    ):
        if callable(user_status_function):
            invoke_callback(
                this_gui,
                str(state_id),
                user_status_function,
                [status] + list(user_status_function_args) + [function_result],  # type: ignore
                str(module_context),
            )
        if e:
            invoke_callback(
                this_gui,
                str(state_id),
                callback_on_exception,
                (
                    str(function_name),
                    e,
                ),
                str(module_context),
            )

    def user_function_in_thread(*uf_args):
        try:
            res = user_function(*uf_args)
            callback_on_status(True, function_result=res)
        except Exception as e:
            callback_on_status(False, e, user_function.__name__)

    def thread_status(name: str, period_s: float, count: int):
        active_thread = next((t for t in threading.enumerate() if t.name == name), None)
        if active_thread:
            callback_on_status(count)
            threading.Timer(period_s, thread_status, (name, period_s, count + 1)).start()

    thread = threading.Thread(target=user_function_in_thread, args=user_function_args)
    thread.start()
    if isinstance(period, int) and period >= 500 and callable(user_status_function):
        thread_status(thread.name, period / 1000.0, 0)
