import typing as t
import warnings

from .gui import Gui
from .state import State


def download(state: State, content: t.Any, name: t.Optional[str] = "", on_action: t.Optional[str] = ""):
    """Donwloads content to the client.

    Args:
        state: the current user state as received in any callback.
        content (Any): file path or file content
        name (optional(str)): file name for the content on the client browser (default to content name)
        on_action (optional(str)): function called when the download starts
    """
    if state and isinstance(state._gui, Gui):
        state._gui._download(content, name, on_action)
    else:
        warnings.warn("'download' function should be called in the context of a callback")


def notify(
    state: State,
    notification_type: str = "I",
    message: str = "",
    browser_notification: t.Optional[bool] = None,
    duration: t.Optional[int] = None,
):
    """Sends a notification to the user interface.

    Args:
        state: the current user state as received in any callback.
        notification_type (optional(string)): The notification type. This can be one of `"success"`, `"info"`, `"warning"` or `"error"`. Default: `"info"`.
            To remove the last notification, set this parameter to the empty string.
        message (string): The text message to display.
        browser_notification (optional(bool)): If set to `True`, the browser will also show the notification.
            If not specified or set to `None`, this parameter will use the value of
            `app_config[browser_notification]`.
        duration (optional(int)): The time, in milliseconds, during which the notification is shown.
            If not specified or set to `None`, this parameter will use the value of
            `app_config[notification_duration]`.

    Note that you can also call this function with _notification_type_ set to the first letter or the alert type
    (ie setting _notification_type_ to `"i"` is equivalent to setting it to `"info"`).
    """
    if state and isinstance(state._gui, Gui):
        state._gui._notify(notification_type, message, browser_notification, duration)
    else:
        warnings.warn("'notify' function should be called in the context of a callback")


def hold_control(
    state: State,
    callback: t.Optional[t.Union[str, t.Callable]] = None,
    message: t.Optional[str] = "Work in Progress...",
):
    """Hold the UI actions (ie prevent user interactions).

    Args:
        state: the current user state as received in any callback.
        action (string | function): The action to be carried on cancel. If empty string or None, no Cancel action will be provided to the user.
        message (string): The message to show. Default: Work in Progress...
    """
    if state and isinstance(state._gui, Gui):
        state._gui._hold_actions(callback, message)
    else:
        warnings.warn("'hold_actions' function should be called in the context of a callback")


def resume_control(state: State):
    """Resume the UI actions (ie allows user interactions).

    Args:
        state: the current user state as received in any callback.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._resume_actions()
    else:
        warnings.warn("'resume_actions' function should be called in the context of a callback")


def navigate(state: State, to: t.Optional[str] = ""):
    """Navigate to a page

    Args:
        state: the current user state as received in any callback.
        to: page to navigate to. Should be a valid page identifier. If ommitted, navigates to the root page.
    """
    if state and isinstance(state._gui, Gui):
        state._gui._navigate(to)
    else:
        warnings.warn("'navigate' function should be called in the context of a callback")
