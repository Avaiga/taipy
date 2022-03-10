from __future__ import annotations

import ast
import builtins
import re
import typing as t
import warnings

if t.TYPE_CHECKING:
    from ..gui import Gui

from . import (
    _get_client_var_name,
    _get_expr_var_name,
    _getscopeattr,
    _getscopeattr_drill,
    _hasscopeattr,
    _setscopeattr,
    _TaipyBase,
)


class _Evaluator:

    # Regex to separate content from inside curly braces when evaluating f string expressions
    __EXPR_RE = re.compile(r"\{(([^\}]*)([^\{]*))\}")
    __EXPR_IS_EXPR = re.compile(r"[^\\][{}]")
    __EXPR_IS_EDGE_CASE = re.compile(r"^\s*{([^}]*)}\s*$")
    __EXPR_VALID_VAR_EDGE_CASE = re.compile(r"^([a-zA-Z\.\_0-9]*)$")
    __EXPR_EDGE_CASE_F_STRING = re.compile(r"[\{]*[a-zA-Z_][a-zA-Z0-9_]*:.+")

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
        self.__global_ctx = default_bindings
        # expr to holders
        self.__expr_to_holders: t.Dict[str, t.Set[t.Type[_TaipyBase]]] = {}

    def get_hash_from_expr(self, expr: str) -> str:
        return self.__expr_to_hash.get(expr, expr)

    def get_expr_from_hash(self, hash: str) -> str:
        return self.__hash_to_expr.get(hash, hash)

    def _is_expression(self, expr: str) -> bool:
        return len(_Evaluator.__EXPR_IS_EXPR.findall(expr)) != 0

    def _fetch_expression_list(self, expr: str) -> t.List:
        return [v[0] for v in _Evaluator.__EXPR_RE.findall(expr)]

    def _analyze_expression(self, gui: Gui, expr: str) -> t.Tuple[t.Dict[str, t.Any], t.List[str]]:
        var_val: t.Dict[str, t.Any] = {}
        var_list: t.List[str] = []
        non_vars = list(self.__global_ctx.keys())
        non_vars.extend(dir(builtins))
        # Get a list of expressions (value that has been wrapped in curly braces {}) and find variables to bind
        for e in self._fetch_expression_list(expr):
            var_name = e.split(sep=".")[0]
            st = ast.parse(e if not _Evaluator.__EXPR_EDGE_CASE_F_STRING.match(e) else 'f"{' + e + '}"')
            args = [arg.arg for node in ast.walk(st) if isinstance(node, ast.arguments) for arg in node.args]
            targets = [
                compr.target.id for node in ast.walk(st) if isinstance(node, ast.ListComp) for compr in node.generators
            ]
            for node in ast.walk(st):
                if isinstance(node, ast.Name):
                    var_name = node.id.split(sep=".")[0]
                    if var_name not in args and var_name not in targets and var_name not in non_vars:
                        try:
                            gui._bind_var(var_name)
                            var_val[var_name] = _getscopeattr_drill(gui, var_name)
                            var_list.append(var_name)
                        except AttributeError as e:
                            warnings.warn(f"Variable '{var_name}' is not defined (in expression '{expr}'): {e}")
        return var_val, var_list

    def __save_expression(
        self,
        gui: Gui,
        expr: str,
        expr_hash: t.Optional[str],
        expr_evaluated: t.Optional[t.Any],
        var_val: t.Dict[str, t.Any],
        var_list: t.List[str],
    ):
        if expr in self.__expr_to_hash:
            if expr_hash is None:
                expr_hash = self.__expr_to_hash[expr]
                gui._bind_var_val(expr_hash, expr_evaluated)
            return expr_hash
        if expr_hash is None:
            expr_hash = self.__expr_to_hash[expr] = _get_expr_var_name(expr)
            gui._bind_var_val(expr_hash, expr_evaluated)
        else:
            self.__expr_to_hash[expr] = expr_hash
        self.__hash_to_expr[expr_hash] = expr
        for var in var_val:
            if var not in self.__global_ctx.keys():
                lst = self.__var_to_expr_list.get(var)
                if lst is None:
                    self.__var_to_expr_list[var] = [expr]
                else:
                    lst.append(expr)
        if expr not in self.__expr_to_var_list:
            self.__expr_to_var_list[expr] = var_list
        return expr_hash

    def evaluate_bind_holder(self, gui: Gui, holder: t.Type[_TaipyBase], expr: str) -> str:
        expr_hash = self.__expr_to_hash.get(expr, "unknownExpr")
        hash_name = self.__get_holder_hash(holder, expr_hash)
        expr_lit = expr.replace("'", "\\'")
        holder_expr = f"{holder.__name__}({expr},'{expr_lit}')"
        self.__evaluate_holder(gui, holder, expr)
        # define dependencies
        a_set = self.__expr_to_holders.get(expr)
        if a_set:
            a_set.add(holder)
        else:
            self.__expr_to_holders[expr] = set([holder])
        self.__expr_to_hash[holder_expr] = hash_name
        # expression is only the first part ...
        expr = expr.split(".")[0]
        self.__expr_to_var_list[holder_expr] = [expr]
        a_list = self.__var_to_expr_list.get(expr)
        if a_list:
            a_list.append(holder_expr)
        else:
            self.__var_to_expr_list[expr] = [holder_expr]
        return hash_name

    def evaluate_holders(self, gui: Gui, expr: str) -> t.List[str]:
        lst = []
        for hld in self.__expr_to_holders.get(expr, []):
            hash = self.__get_holder_hash(hld, self.__expr_to_hash.get(expr))
            self.__evaluate_holder(gui, hld, expr)
            lst.append(hash)
        return lst

    @staticmethod
    def __get_holder_hash(holder: t.Type[_TaipyBase], expr_hash: str) -> str:
        return f"{holder.get_hash()}_{_get_client_var_name(expr_hash)}"

    def __evaluate_holder(self, gui: Gui, holder: t.Type[_TaipyBase], expr: str) -> _TaipyBase:
        try:
            expr_hash = self.__expr_to_hash.get(expr, "unknownExpr")
            holder_hash = self.__get_holder_hash(holder, expr_hash)
            expr_value = _getscopeattr_drill(gui, expr_hash)
            holder_value = _getscopeattr(gui, holder_hash, None)
            if not isinstance(holder_value, _TaipyBase):
                holder_value = holder(expr_value, expr_hash)
                _setscopeattr(gui, holder_hash, holder_value)
            else:
                holder_value.set(expr_value)
            return holder_value
        except Exception as e:
            warnings.warn(f"Cannot evaluate expression {holder.__name__}({expr_hash},'{expr_hash}') for {expr}: {e}")
        return None

    def evaluate_expr(self, gui: Gui, expr: str) -> t.Any:
        if not self._is_expression(expr):
            return expr
        var_val, var_list = self._analyze_expression(gui, expr)
        expr_hash = None
        is_edge_case = False

        # The expr_string is placed here in case expr get replaced by edge case
        expr_string = 'f"' + expr.replace('"', '\\"') + '"'
        # simplify expression if it only contains var_name
        m = _Evaluator.__EXPR_IS_EDGE_CASE.match(expr)
        if m and not _Evaluator.__EXPR_EDGE_CASE_F_STRING.match(expr):
            expr = m.group(1)
            expr_hash = expr if _Evaluator.__EXPR_VALID_VAR_EDGE_CASE.match(expr) else None
            is_edge_case = True
        # validate whether expression has already been evaluated
        if expr in self.__expr_to_hash and _hasscopeattr(gui, self.__expr_to_hash[expr]):
            return self.__expr_to_hash[expr]
        try:
            # evaluate expressions
            ctx = {}
            ctx.update(self.__global_ctx)
            # entries in var_val are not always seen (NameError) when passed as locals
            ctx.update(var_val)
            expr_evaluated = eval(expr_string if not is_edge_case else expr, ctx)
        except Exception as e:
            warnings.warn(f"Cannot evaluate expression '{expr if is_edge_case else expr_string}': {e}")
            expr_evaluated = None
        # save the expression if it needs to be re-evaluated
        return self.__save_expression(gui, expr, expr_hash, expr_evaluated, var_val, var_list)

    def re_evaluate_expr(self, gui: Gui, var_name: str) -> t.Set[str]:
        """
        This function will execute when the _update_var function is handling
        an expression with only a single variable
        """
        modified_vars: t.Set[str] = set()
        var_name = var_name.split(".")[0]
        if var_name not in self.__var_to_expr_list.keys():
            return modified_vars
        for expr in self.__var_to_expr_list[var_name]:
            if expr == var_name:
                continue
            hash_expr = self.__expr_to_hash.get(expr, "UnknownExpr")
            expr_var_list = self.__expr_to_var_list.get(expr)  # ["x", "y"]
            if expr_var_list is None:
                warnings.warn(f"Someting is amiss with expression list for {expr}")
                continue
            eval_dict = {v: _getscopeattr_drill(gui, v) for v in expr_var_list}

            if self._is_expression(expr):
                expr_string = 'f"' + expr.replace('"', '\\"') + '"'
            else:
                expr_string = expr

            try:
                ctx = {}
                ctx.update(self.__global_ctx)
                ctx.update(eval_dict)
                expr_evaluated = eval(expr_string, ctx)
                _setscopeattr(gui, hash_expr, expr_evaluated)
            except Exception as e:
                warnings.warn(f"Problem evaluating {expr_string}: {e}")

            # refresh holders if any
            for h in self.__expr_to_holders.get(expr, []):
                holder_hash = self.__get_holder_hash(h, self.get_hash_from_expr(expr))
                if holder_hash not in modified_vars:
                    _setscopeattr(gui, holder_hash, self.__evaluate_holder(gui, h, expr))
                    modified_vars.add(holder_hash)

            modified_vars.add(hash_expr)
        return modified_vars
