"""Flask plugin. Includes a path helper that allows you to pass a view
function to `path`. Inspects URL rules and view docstrings.

Passing a view function::

    from flask import Flask

    app = Flask(__name__)

    @app.route('/gists/<gist_id>')
    def gist_detail(gist_id):
        '''Gist detail view.
        ---
        x-extension: metadata
        get:
            responses:
                200:
                    schema:
                        $ref: '#/definitions/Gist'
        '''
        return 'detail for gist {}'.format(gist_id)

    with app.test_request_context():
        spec.path(view=gist_detail)
    print(spec.to_dict()['paths'])
    # {'/gists/{gist_id}': {'get': {'responses': {200: {'schema': {'$ref': '#/definitions/Gist'}}}},
    #                  'x-extension': 'metadata'}}

Passing a method view function::

    from flask import Flask
    from flask.views import MethodView

    app = Flask(__name__)

    class GistApi(MethodView):
        '''Gist API.
        ---
        x-extension: metadata
        '''
        def get(self):
           '''Gist view
           ---
           responses:
               200:
                   schema:
                       $ref: '#/definitions/Gist'
           '''
           pass

        def post(self):
           pass

    method_view = GistApi.as_view('gists')
    app.add_url_rule("/gists", view_func=method_view)
    with app.test_request_context():
        spec.path(view=method_view)

    # Alternatively, pass in an app object as a kwarg
    # spec.path(view=method_view, app=app)

    print(spec.to_dict()['paths'])
    # {'/gists': {'get': {'responses': {200: {'schema': {'$ref': '#/definitions/Gist'}}}},
    #             'post': {},
    #             'x-extension': 'metadata'}}


"""  # noqa: E501
import re
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from apispec import BasePlugin, yaml_utils
from apispec.exceptions import APISpecError
from flask import Flask, current_app
from flask.views import MethodView
from werkzeug.routing import Rule

if TYPE_CHECKING:
    from flask.typing import RouteCallable


# from flask-restplus
RE_URL = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>")


class FlaskPlugin(BasePlugin):
    """APISpec plugin for Flask"""

    @staticmethod
    def flaskpath2openapi(path: str) -> str:
        """Convert a Flask URL rule to an OpenAPI-compliant path.

        :param str path: Flask path template.
        """
        return RE_URL.sub(r"{\1}", path)

    @staticmethod
    def _rule_for_view(
        view: Union[Callable[..., Any], "RouteCallable"],
        app: Optional[Flask] = None,
    ) -> Rule:
        if app is None:
            app = current_app

        view_funcs = app.view_functions
        endpoint = None
        for ept, view_func in view_funcs.items():
            if view_func == view:
                endpoint = ept
        if not endpoint:
            raise APISpecError(f"Could not find endpoint for view {view}")

        # WARNING: Assume 1 rule per view function for now
        rule = app.url_map._rules_by_endpoint[endpoint][0]
        return rule

    def path_helper(
        self,
        path: Optional[str] = None,
        operations: Optional[dict] = None,
        parameters: Optional[List[dict]] = None,
        *,
        view: Optional[Union[Callable[..., Any], "RouteCallable"]] = None,
        app: Optional[Flask] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """Path helper that allows passing a Flask view function."""
        assert view is not None
        assert operations is not None

        rule = self._rule_for_view(view, app=app)
        view_doc = view.__doc__ or ""
        doc_operations = yaml_utils.load_operations_from_docstring(view_doc)
        operations.update(doc_operations)
        if hasattr(view, "view_class") and issubclass(view.view_class, MethodView):  # noqa: E501
            # method attribute is dynamically added, which is supported by mypy
            for method in view.methods:  # type:ignore[union-attr]
                if rule.methods and method in rule.methods:
                    method_name = method.lower()
                    method = getattr(view.view_class, method_name)
                    method_docstring = method.__doc__ or ""
                    operations[method_name] = yaml_utils.load_yaml_from_docstring(  # noqa: E501
                        method_docstring
                    )
        return self.flaskpath2openapi(rule.rule)
