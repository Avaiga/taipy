import typing as t

from _typeshed import Incomplete
from flask import Flask

from .config import Config
from .config import ServerConfig as ServerConfig
from .config import Stylekit as Stylekit
from .extension.library import ElementLibrary
from .page import Page
from .partial import Partial

class _DoNotUpdate: ...

class Gui:
    on_action: Incomplete
    on_change: Incomplete
    on_init: Incomplete
    on_navigate: Incomplete
    on_exception: Incomplete
    on_status: Incomplete
    on_user_content: Incomplete
    def __init__(
        self,
        page: t.Optional[t.Union[str, Page]] = ...,
        pages: t.Optional[dict] = ...,
        css_file: t.Optional[str] = ...,
        path_mapping: t.Optional[dict] = ...,
        env_filename: t.Optional[str] = ...,
        libraries: t.Optional[t.List[ElementLibrary]] = ...,
        flask: t.Optional[Flask] = ...,
    ) -> None: ...
    @staticmethod
    def add_library(library: ElementLibrary) -> None: ...
    @staticmethod
    def add_shared_variable(*names: str) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_value, traceback): ...
    def add_page(self, name: str, page: t.Union[str, Page], style: t.Optional[str] = ...) -> None: ...
    def add_pages(self, pages: t.Optional[t.Union[t.Mapping[str, t.Union[str, Page]], str]] = ...) -> None: ...
    def add_partial(self, page: t.Union[str, Page]) -> Partial: ...
    def load_config(self, config: Config) -> None: ...
    def broadcast(self, name: str, value: t.Any): ...
    def get_flask_app(self) -> Flask: ...
    state: Incomplete
    def run(
        self,
        allow_unsafe_werkzeug: bool = ...,
        async_mode: str = ...,
        change_delay: t.Optional[int] = ...,
        chart_dark_template: t.Optional[t.Dict[str, t.Any]] = ...,
        base_url: t.Optional[str] = ...,
        dark_mode: bool = ...,
        dark_theme: t.Optional[t.Dict[str, t.Any]] = ...,
        data_url_max_size: t.Optional[int] = ...,
        debug: bool = ...,
        extended_status: bool = ...,
        favicon: t.Optional[str] = ...,
        flask_log: bool = ...,
        host: str = ...,
        light_theme: t.Optional[t.Dict[str, t.Any]] = ...,
        margin: t.Optional[str] = ...,
        ngrok_token: str = ...,
        notebook_proxy: bool = ...,
        notification_duration: int = ...,
        propagate: bool = ...,
        run_browser: bool = ...,
        run_in_thread: bool = ...,
        run_server: bool = ...,
        server_config: t.Optional[ServerConfig] = ...,
        single_client: bool = ...,
        system_notification: bool = ...,
        theme: t.Optional[t.Dict[str, t.Any]] = ...,
        time_zone: t.Optional[str] = ...,
        title: t.Optional[str] = ...,
        stylekit: t.Union[bool, Stylekit] = ...,
        upload_folder: t.Optional[str] = ...,
        use_arrow: bool = ...,
        use_reloader: bool = ...,
        watermark: t.Optional[str] = ...,
        webapp_path: t.Optional[str] = ...,
        port: int = ...,
    ) -> t.Optional[Flask]: ...
    def reload(self) -> None: ...
    def stop(self) -> None: ...
