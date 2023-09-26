# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import annotations

import ast
import builtins
import re
import typing as t

from .._warnings import _warn

if t.TYPE_CHECKING:
    from ..gui import Gui

from . import (
    _get_client_var_name,
    _get_expr_var_name,
    _getscopeattr,
    _getscopeattr_drill,
    _hasscopeattr,
    _MapDict,
    _setscopeattr,
    _setscopeattr_drill,
    _TaipyBase,
    _variable_decode,
    _variable_encode,
)


class _Evaluator:
    # Regex to separate content from inside curly braces when evaluating f string expressions
    __EXPR_RE = re.compile(r"\{(([^\}]*)([^\{]*))\}")
    __EXPR_IS_EXPR = re.compile(r"[^\\][{}]")
    __EXPR_IS_EDGE_CASE = re.compile(r"^\s*{([^}]*)}\s*$")
    __EXPR_VALID_VAR_EDGE_CASE = re.compile(r"^([a-zA-Z\.\_0-9\[\]]*)$")
    __EXPR_EDGE_CASE_F_STRING = re.compile(r"[\{]*[a-zA-Z_][a-zA-Z0-9_]*:.+")
    __IS_TAIPYEXPR_RE = re.compile(r"TpExPr_(.*)")

    def __init__(self, default_bindings: t.Dict[str, t.Any], shared_variable: t.List[str]) -> None:
        # key = expression, value = hashed value of the expression
        self.__expr_to_hash: t.Dict[str, str] = {}
        # key = hashed value of the expression, value = expression
        self.__hash_to_expr: t.Dict[str, str] = {}
        # key = variable name of the expression, key = list of related expressions
        # ex: {x + y}
        # "x_TPMDL_0": ["{x + y}"],
        # "y_TPMDL_0": ["{x + y}"],
        self.__var_to_expr_list: t.Dict[str, t.List[str]] = {}
        # key = expression, value = list of related variables
        # "{x + y}": {"x": "x_TPMDL_", "y": "y_TPMDL_0"}
        self.__expr_to_var_map: t.Dict[str, t.Dict[str, str]] = {}
        # instead of binding everywhere the types
        self.__global_ctx = default_bindings
        # expr to holders
        self.__expr_to_holders: t.Dict[str, t.Set[t.Type[_TaipyBase]]] = {}
        # shared variables between multiple clients
        self.__shared_variable = shared_variable

    @staticmethod
    def _expr_decode(s: str):
        return str(result[1]) if (result := _Evaluator.__IS_TAIPYEXPR_RE.match(s)) else s

    def get_hash_from_expr(self, expr: str) -> str:
        return self.__expr_to_hash.get(expr, expr)

    def get_expr_from_hash(self, hash_val: str) -> str:
        return self.__hash_to_expr.get(hash_val, hash_val)

    def get_shared_variables(self) -> t.List[str]:
        return self.__shared_variable

    def _is_expression(self, expr: str) -> bool:
        return len(_Evaluator.__EXPR_IS_EXPR.findall(expr)) != 0

    def _fetch_expression_list(self, expr: str) -> t.List:
        return [v[0] for v in _Evaluator.__EXPR_RE.findall(expr)]

    def _analyze_expression(self, gui: Gui, expr: str) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, str]]:
        var_val: t.Dict[str, t.Any] = {}
        var_map: t.Dict[str, str] = {}
        non_vars = list(self.__global_ctx.keys())
        non_vars.extend(dir(builtins))
        # Get a list of expressions (value that has been wrapped in curly braces {}) and find variables to bind
        for e in self._fetch_expression_list(expr):
            var_name = e.split(sep=".")[0]
            st = ast.parse('f"{' + e + '}"' if _Evaluator.__EXPR_EDGE_CASE_F_STRING.match(e) else e)
            args = [arg.arg for node in ast.walk(st) if isinstance(node, ast.arguments) for arg in node.args]
            targets = [
                compr.target.id for node in ast.walk(st) if isinstance(node, ast.ListComp) for compr in node.generators  # type: ignore
            ]
            for node in ast.walk(st):
                if isinstance(node, ast.Name):
                    var_name = node.id.split(sep=".")[0]
                    if var_name not in args and var_name not in targets and var_name not in non_vars:
                        try:
                            encoded_var_name = gui._bind_var(var_name)
                            var_val[var_name] = _getscopeattr_drill(gui, encoded_var_name)
                            var_map[var_name] = encoded_var_name
                        except AttributeError as e:
                            _warn(f"Variable '{var_name}' is not defined (in expression '{expr}')", e)
        return var_val, var_map

    def __save_expression(
        self,
        gui: Gui,
        expr: str,
        expr_hash: t.Optional[str],
        expr_evaluated: t.Optional[t.Any],
        var_map: t.Dict[str, str],
    ):
        if expr in self.__expr_to_hash:
            expr_hash = self.__expr_to_hash[expr]
            gui._bind_var_val(expr_hash, expr_evaluated)
            return expr_hash
        if expr_hash is None:
            expr_hash = _get_expr_var_name(expr)
        else:
            # edge case, only a single variable
            expr_hash = f"tpec_{_get_client_var_name(expr)}"
        self.__expr_to_hash[expr] = expr_hash
        gui._bind_var_val(expr_hash, expr_evaluated)
        self.__hash_to_expr[expr_hash] = expr
        for var in var_map.values():
            if var not in self.__global_ctx.keys():
                lst = self.__var_to_expr_list.get(var)
                if lst is None:
                    self.__var_to_expr_list[var] = [expr]
                else:
                    lst.append(expr)
        if expr not in self.__expr_to_var_map:
            self.__expr_to_var_map[expr] = var_map
        # save expr_hash to shared variable if valid
        for encoded_var_name in var_map.values():
            var_name, module_name = _variable_decode(encoded_var_name)
            # only variables in the main module with be taken into account
            if module_name is not None and module_name != gui._get_default_module_name():
                continue
            if var_name in self.__shared_variable:
                self.__shared_variable.append(expr_hash)
        return expr_hash

    def evaluate_bind_holder(self, gui: Gui, holder: t.Type[_TaipyBase], expr: str) -> str:
        expr_hash = self.__expr_to_hash.get(expr, "unknownExpr")
        hash_name = self.__get_holder_hash(holder, expr_hash)
        expr_lit = expr.replace("'", "\\'")
        holder_expr = f"{holder.__name__}({expr},'{expr_lit}')"
        self.__evaluate_holder(gui, holder, expr)
        if a_set := self.__expr_to_holders.get(expr):
            a_set.add(holder)
        else:
            self.__expr_to_holders[expr] = {holder}
        self.__expr_to_hash[holder_expr] = hash_name
        # expression is only the first part ...
        expr = expr.split(".")[0]
        self.__expr_to_var_map[holder_expr] = {expr: expr}
        if a_list := self.__var_to_expr_list.get(expr):
            if holder_expr not in a_list:
                a_list.append(holder_expr)
        else:
            self.__var_to_expr_list[expr] = [holder_expr]
        return hash_name

    def evaluate_holders(self, gui: Gui, expr: str) -> t.List[str]:
        lst = []
        for hld in self.__expr_to_holders.get(expr, []):
            hash_val = self.__get_holder_hash(hld, self.__expr_to_hash.get(expr, ""))
            self.__evaluate_holder(gui, hld, expr)
            lst.append(hash_val)
        return lst

    @staticmethod
    def __get_holder_hash(holder: t.Type[_TaipyBase], expr_hash: str) -> str:
        return f"{holder.get_hash()}_{_get_client_var_name(expr_hash)}"

    def __evaluate_holder(self, gui: Gui, holder: t.Type[_TaipyBase], expr: str) -> t.Optional[_TaipyBase]:
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
            _warn(f"Cannot evaluate expression {holder.__name__}({expr_hash},'{expr_hash}') for {expr}", e)
        return None

    def evaluate_expr(self, gui: Gui, expr: str) -> t.Any:
        if not self._is_expression(expr):
            return expr
        var_val, var_map = self._analyze_expression(gui, expr)
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
        module_name = gui._get_locals_context()
        not_encoded_expr = expr
        expr = f"TpExPr_{_variable_encode(expr, module_name)}"
        if expr in self.__expr_to_hash and _hasscopeattr(gui, self.__expr_to_hash[expr]):
            return self.__expr_to_hash[expr]
        try:
            # evaluate expressions
            ctx: t.Dict[str, t.Any] = {}
            ctx.update(self.__global_ctx)
            # entries in var_val are not always seen (NameError) when passed as locals
            ctx.update(var_val)
            expr_evaluated = eval(not_encoded_expr if is_edge_case else expr_string, ctx)
        except Exception as e:
            _warn(f"Cannot evaluate expression '{not_encoded_expr if is_edge_case else expr_string}'", e)
            expr_evaluated = None
        # save the expression if it needs to be re-evaluated
        return self.__save_expression(gui, expr, expr_hash, expr_evaluated, var_map)

    def refresh_expr(self, gui: Gui, var_name: str, holder: t.Optional[_TaipyBase]):
        """
        This function will execute when the __request_var_update function receive a refresh order
        """
        expr = self.__hash_to_expr.get(var_name)
        if expr:
            expr_decoded, _ = _variable_decode(expr)
            var_map = self.__expr_to_var_map.get(expr, {})
            eval_dict = {k: _getscopeattr_drill(gui, gui._bind_var(v)) for k, v in var_map.items()}
            if self._is_expression(expr_decoded):
                expr_string = 'f"' + _variable_decode(expr)[0].replace('"', '\\"') + '"'
            else:
                expr_string = expr_decoded
            try:
                ctx: t.Dict[str, t.Any] = {}
                ctx.update(self.__global_ctx)
                ctx.update(eval_dict)
                expr_evaluated = eval(expr_string, ctx)
                _setscopeattr(gui, var_name, expr_evaluated)
                if holder is not None:
                    holder.set(expr_evaluated)
            except Exception as e:
                _warn(f"Exception raised evaluating {expr_string}", e)

    def re_evaluate_expr(self, gui: Gui, var_name: str) -> t.Set[str]:
        """
        This function will execute when the _update_var function is handling
        an expression with only a single variable
        """
        modified_vars: t.Set[str] = set()
        # Verify that the current hash is an edge case one (only a single variable inside the original expression)
        if var_name.startswith("tp_"):
            return modified_vars
        expr_original = None
        # if var_name starts with tpec_ --> it is an edge case with modified var
        if var_name.startswith("tpec_"):
            # backup for later reference
            var_name_original = var_name
            expr_original = self.__hash_to_expr[var_name]
            temp_expr_var_map = self.__expr_to_var_map[expr_original]
            if len(temp_expr_var_map) <= 1:
                # since this is an edge case --> only 1 item in the dict and that item is the original var
                for v in temp_expr_var_map.values():
                    var_name = v
                # construct correct var_path to reassign values
                var_name_full, _ = _variable_decode(expr_original)
                var_name_full = var_name_full.split(".")
                var_name_full[0] = var_name
                var_name_full = ".".join(var_name_full)
                _setscopeattr_drill(gui, var_name_full, _getscopeattr(gui, var_name_original))
            else:
                # multiple key-value pair in expr_var_map --> expr is special case a["b"]
                key = ""
                for v in temp_expr_var_map.values():
                    if isinstance(_getscopeattr(gui, v), _MapDict):
                        var_name = v
                    else:
                        key = v
                if key == "":
                    return modified_vars
                _setscopeattr_drill(gui, f"{var_name}.{_getscopeattr(gui, key)}", _getscopeattr(gui, var_name_original))
        # A middle check to see if var_name is from _MapDict
        if "." in var_name:
            var_name = var_name[: var_name.index(".")]
        # otherwise, thar var_name is correct and doesn't require any resolution
        if var_name not in self.__var_to_expr_list:
            # _warn("{var_name} not found.")
            return modified_vars
        # refresh expressions and holders
        for expr in self.__var_to_expr_list[var_name]:
            expr_decoded, _ = _variable_decode(expr)
            hash_expr = self.__expr_to_hash.get(expr, "UnknownExpr")
            if expr != var_name and not expr.startswith(_TaipyBase._HOLDER_PREFIX):
                expr_var_map = self.__expr_to_var_map.get(expr)  # ["x", "y"]
                if expr_var_map is None:
                    _warn(f"Something is amiss with expression list for {expr}.")
                else:
                    eval_dict = {k: _getscopeattr_drill(gui, gui._bind_var(v)) for k, v in expr_var_map.items()}
                    if self._is_expression(expr_decoded):
                        expr_string = 'f"' + _variable_decode(expr)[0].replace('"', '\\"') + '"'
                    else:
                        expr_string = expr_decoded
                    try:
                        ctx: t.Dict[str, t.Any] = {}
                        ctx.update(self.__global_ctx)
                        ctx.update(eval_dict)
                        expr_evaluated = eval(expr_string, ctx)
                        _setscopeattr(gui, hash_expr, expr_evaluated)
                    except Exception as e:
                        _warn(f"Exception raised evaluating {expr_string}", e)
            # refresh holders if any
            for h in self.__expr_to_holders.get(expr, []):
                holder_hash = self.__get_holder_hash(h, self.get_hash_from_expr(expr))
                if holder_hash not in modified_vars:
                    _setscopeattr(gui, holder_hash, self.__evaluate_holder(gui, h, expr))
                    modified_vars.add(holder_hash)
            modified_vars.add(hash_expr)
        return modified_vars
