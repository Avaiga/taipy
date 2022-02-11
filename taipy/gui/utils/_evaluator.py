from __future__ import annotations

import ast
import builtins
import re
import typing as t
import warnings
from operator import attrgetter

import __main__

from . import _get_expr_var_name, attrsetter, get_client_var_name

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Evaluator:

    # Regex to separate content from inside curly braces when evaluating f string expressions
    __EXPR_RE = re.compile(r"\{(.*?)\}")
    __EXPR_IS_EXPR = re.compile(r"[^\\][{}]")
    __EXPR_IS_EDGE_CASE = re.compile(r"^\s*{([^}]*)}\s*$")
    __EXPR_VALID_VAR_EDGE_CASE = re.compile(r"^([a-zA-Z\.\_0-9]*)$")

    def __init__(self, default_bindings: t.Dict[str, t.Any]) -> None:
        # key = expression, value = hashed value of the expression
        self.__expr_to_hash: t.Dict[str, str] = {}
        # key = hashed value of the expression, value = expression
        self.__hash_to_expr: t.Dict[str, str] = {}
        # key = variable name of the expression, key = list of related expressions
        # ex: {x + y}
        # "x": ["{x + y}"],
        # "y": ["{x + y}"],
        self.__var_to_expr_list: t.Dict[str, t.List[str]] = {}
        # key = expression, value = list of related variables
        # "{x + y}": ["x", "y"]
        self.__expr_to_var_list: t.Dict[str, t.List[str]] = {}
        # instead of binding everywhere the types
        self.__default_bindings = default_bindings
        # expr to holders
        self.__expr_to_holders: t.Dict[str, t.Set[str]] = {}

    def get_hash_from_expr(self, expr: str) -> str:
        return self.__expr_to_hash.get(expr, expr)

    def get_expr_from_hash(self, hash: str) -> str:
        return self.__hash_to_expr.get(hash, hash)

    def _is_expression(self, expr: str) -> bool:
        return len(_Evaluator.__EXPR_IS_EXPR.findall(expr)) != 0

    def _fetch_expression_list(self, expr: str) -> t.List:
        return _Evaluator.__EXPR_RE.findall(expr)

    def _analyze_expression(self, gui: Gui, expr: str) -> t.Tuple[t.Dict[str, t.Any], t.List[str]]:
        var_val: t.Dict[str, t.Any] = {}
        var_list: t.List[str] = []
        # Get a list of expressions (value that has been wrapped in curly braces {}) and find variables to bind
        for e in self._fetch_expression_list(expr):
            st = ast.parse(e)
            args = []
            for node in ast.walk(st):
                if isinstance(node, ast.arguments):
                    args = [x.arg for x in node.args]
                elif isinstance(node, ast.Name):
                    var_name = node.id.split(sep=".")[0]
                    if (
                        var_name not in args
                        and var_name not in dir(builtins)
                        and var_name not in self.__default_bindings.keys()
                    ):
                        gui.bind_var(var_name)
                        try:
                            var_val[var_name] = attrgetter(var_name)(gui._get_data_scope())
                            var_list.append(var_name)
                        except AttributeError:
                            warnings.warn(f"Variable '{var_name}' is not defined (in expression '{expr}')")
        return var_val, var_list

    def __save_expression(
        self,
        gui: Gui,
        expr: str,
        expr_hash: t.Union[None, str],
        expr_evaluated: t.Union[t.Any, None],
        var_val: t.Dict[str, t.Any],
        var_list: t.List[str],
    ):
        if expr in self.__expr_to_hash:
            if expr_hash is None:
                expr_hash = self.__expr_to_hash[expr]
                gui.bind_var_val(expr_hash, expr_evaluated)
            return expr_hash
        if expr_hash is None:
            expr_hash = self.__expr_to_hash[expr] = _get_expr_var_name(expr)
            gui.bind_var_val(expr_hash, expr_evaluated)
        else:
            self.__expr_to_hash[expr] = expr_hash
        self.__hash_to_expr[expr_hash] = expr
        for var in var_val:
            if var not in self.__default_bindings.keys():
                lst = self.__var_to_expr_list.get(var)
                if lst is None:
                    self.__var_to_expr_list[var] = [expr]
                else:
                    lst.append(expr)
        if expr not in self.__expr_to_var_list:
            self.__expr_to_var_list[expr] = var_list
        return expr_hash

    def evaluate_bind_holder(self, gui: Gui, holder_name: str, expr: str) -> str:
        expr_hash = self.__expr_to_hash.get(expr)
        expr_holder = f"{holder_name}({expr_hash},'{expr_hash}')"
        a_set = self.__expr_to_holders.get(expr)
        if a_set:
            a_set.add(expr_holder)
        else:
            self.__expr_to_holders[expr] = set([expr_holder])
        hash_name = f"{holder_name}_{get_client_var_name(expr_hash)}"
        self.__expr_to_hash[expr_holder] = hash_name
        a_list = self.__var_to_expr_list.get(expr)
        if a_list:
            a_list.append(expr_holder)
        else:
            self.__var_to_expr_list[expr] = [expr_holder]
        var_val, var_list = self._analyze_expression(gui, f"{{{expr_holder}}}")
        self.__expr_to_var_list[expr_holder] = var_list
        setattr(gui._get_data_scope(), hash_name, self.__evaluate_holder(expr_holder, var_val))
        return hash_name

    def evaluate_holders(self, gui: Gui, expr: str) -> t.List[str]:
        lst = []
        for hld in self.__expr_to_holders.get(expr, []):
            hash = self.__expr_to_hash.get(hld)
            var_val, _ = self._analyze_expression(gui, f"{{{hld}}}")
            setattr(gui._get_data_scope(), hash, self.__evaluate_holder(hld, var_val))
            lst.append(hash)
        return lst

    def __evaluate_holder(self, expr_holder: str, var_val: t.Dict[str, t.List[str]]) -> t.Any:
        try:
            # evaluate expressions
            return eval(expr_holder, self.__default_bindings, var_val)
        except Exception:
            warnings.warn(f"Cannot evaluate expression '{expr_holder}'")
        return None

    def evaluate_expr(self, gui: Gui, expr: str, bind=False) -> t.Any:
        if not self._is_expression(expr):
            return expr
        var_val, var_list = self._analyze_expression(gui, expr)
        expr_hash = None
        is_edge_case = False

        # The expr_string is placed here in case expr get replaced by edge case
        expr_string = 'f"' + expr.replace('"', '\\"') + '"'
        # simplify expression if it only contains var_name
        m = _Evaluator.__EXPR_IS_EDGE_CASE.match(expr)
        if m:
            expr = m.group(1)
            expr_hash = expr if _Evaluator.__EXPR_VALID_VAR_EDGE_CASE.match(expr) else None
            is_edge_case = True
        # validate whether expression has already been evaluated
        if expr in self.__expr_to_hash and hasattr(gui._get_data_scope(), self.__expr_to_hash[expr]):
            return self.__expr_to_hash[expr]
        try:
            # evaluate expressions
            expr_evaluated = eval(expr_string if not is_edge_case else expr, self.__default_bindings, var_val)
        except Exception:
            warnings.warn(f"Cannot evaluate expression '{expr if is_edge_case else expr_string}'")
            expr_evaluated = None
        if bind:
            gui.bind_var_val(expr_hash, expr_evaluated)
        # save the expression if it needs to be re-evaluated
        return self.__save_expression(gui, expr, expr_hash, expr_evaluated, var_val, var_list)

    def re_evaluate_expr(self, gui: Gui, var_name: str) -> t.Set[str]:
        """
        This function will execute when the _update_var function is handling
        an expression with only a single variable
        """
        modified_vars: t.Set[str] = set()
        if var_name not in self.__var_to_expr_list.keys():
            return modified_vars
        for expr in self.__var_to_expr_list[var_name]:
            if expr == var_name:
                continue
            hash_expr = self.__expr_to_hash[expr]
            expr_var_list = self.__expr_to_var_list[expr]  # ["x", "y"]
            eval_dict = {v: attrgetter(v)(gui._get_data_scope()) for v in expr_var_list}

            if self._is_expression(expr):
                expr_string = 'f"' + expr.replace('"', '\\"') + '"'
            else:
                expr_string = expr

            try:
                expr_evaluated = eval(expr_string, self.__default_bindings, eval_dict)
                attrsetter(gui._get_data_scope(), hash_expr, expr_evaluated)
            except Exception as e:
                warnings.warn(f"Problem evaluating {expr_string}: {e}")
            modified_vars.add(hash_expr)
        return modified_vars
