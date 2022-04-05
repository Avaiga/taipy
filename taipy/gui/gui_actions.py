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
