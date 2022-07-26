# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
import warnings

from .gui import Gui
from .state import State


def download(state: State, content: t.Any, name: t.Optional[str] = "", on_action: t.Optional[str] = ""):
    """Download content to the client.

    Arguments:
        state (State^): The current user state as received in any callback.
        content: File path or file content.
        name: File name for the content on the client browser (default to content name).
        on_action: Function called when the download starts.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._download(content, name, on_action)
    else:
        warnings.warn("'download()' must be called in the context of a callback")


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
        notification_type: The notification type. This can be one of _"success"_, _"info"_,
            _"warning"_, or _"error"_.<br/>
            To remove the last notification, set this parameter to the empty string.
        message: The text message to display.
        system_notification: If True, the system will also show the notification.
            If not specified or set to None, this parameter will use the value of
            _configuration[system_notification]_.
        duration: The time, in milliseconds, during which the notification is shown.
            If not specified or set to None, this parameter will use the value of
            _configuration[notification_duration]_.

    Note that you can also call this function with _notification_type_ set to the first letter
    or the alert type (ie setting _notification_type_ to "i" is equivalent to setting it to
    "info").

    If _system_notification_ is set to True, then the browser requests the system
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
        warnings.warn("'notify()' must be called in the context of a callback")


def hold_control(
    state: State,
    callback: t.Optional[t.Union[str, t.Callable]] = None,
    message: t.Optional[str] = "Work in Progress...",
):
    """Hold the User Interface actions.

    When the User Interface is held, users cannot interact with visual elements.<br/>
    The application must call `resume_control()^` so that users can interact again
    with the visual elements.

    Arguments:
        state (State^): The current user state as received in any callback.
        callback (Optional[Union[str, Callable]]): the function to be called if the user
            chooses to cancel.<br/>
            If empty or None, no cancel action is provided to the user.
        message: the message to show.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._hold_actions(callback, message)
    else:
        warnings.warn("'hold_actions()' must be called in the context of a callback")


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
        warnings.warn("'resume_actions()' must be called in the context of a callback")


def navigate(state: State, to: t.Optional[str] = ""):
    """Navigate to a page.

    Arguments:
        state (State^): The current user state as received in any callback.
        to: The name of the page to navigate to. This must be a valid page identifier.
            If ommitted, the application navigates to the root page.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._navigate(to)
    else:
        warnings.warn("'navigate()' must be called in the context of a callback")


def get_context_id(state: State) -> t.Optional[str]:
    """Get the current context identifier (as needed for serializable callbacks).

    Arguments:
        state (State^): The current user state as received in any callback.
    """
    if state and isinstance(state._gui, Gui):
        return state._gui._get_client_id()
    return None


def get_module_name_from_state(state: State) -> t.Optional[str]:
    """Get the module name that triggered a callback.

    Pages can be defined in different modules yet share callbacks declared elsewhere (typically, the
    application's main module).

    This function returns the name of the module where the page (that holds the control that triggered the
    callback) was declared.  This lets applications implement different behaviors depending on what page
    is involved.

    This function must be called only in the body of a callback function.

    Arguments:

        state: (State^): The `State` instance, which is an argument of the callback function.

    Returns:

        str: The name of the module that holds the definition of the page containing the control that
            triggered this callback.
    """
    if state and isinstance(state._gui, Gui):
        return state._gui._get_locals_context()
    return None


def invoke_state_callback(
    gui: Gui, context_id: str, user_callback: t.Callable, args: t.Union[t.Tuple, t.List]
) -> t.Any:
    """Invoke a user callback with context.

    Arguments:
        gui (Gui^): The current gui instance.
        context_id: The context id as returned by get_context_id()^.
        user_callback (Callable[[State, ...], None): The user-defined function that is invoked. The first parameter of this function must be a `State^`.
        args: The remaining arguments, as a List or a Tuple.
    """
    if isinstance(gui, Gui):
        return gui._call_user_callback(context_id, user_callback, list(args))
    else:
        warnings.warn("'invoke_state_callback()' must be called with a valid Gui instance")
