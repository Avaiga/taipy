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

import argparse
import sys as _sys
from argparse import _UNRECOGNIZED_ARGS_ATTR, SUPPRESS, ArgumentError, Namespace


class _ArgumentParser(argparse.ArgumentParser):
    def parse_known_args(self, args=None, namespace=None, exit_on_error=False):
        """Copy from argparse.ArgumentParser.parse_known_args() method.

        The only different is the exit_on_error attribute is replaced by a exit_on_error parameter
        because Python 3.8 doesn't have exit_on_error attribute.
        """
        if args is None:
            # args default to the system args
            args = _sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)

        # default Namespace built from parser defaults
        if namespace is None:
            namespace = Namespace()

        # add any action defaults that aren't present
        for action in self._actions:
            if action.dest is not SUPPRESS:
                if not hasattr(namespace, action.dest):
                    if action.default is not SUPPRESS:
                        setattr(namespace, action.dest, action.default)

        # add any parser defaults that aren't present
        for dest in self._defaults:
            if not hasattr(namespace, dest):
                setattr(namespace, dest, self._defaults[dest])

        # parse the arguments and exit if there are any errors
        if exit_on_error:
            try:
                namespace, args = self._parse_known_args(args, namespace)
            except ArgumentError:
                err = _sys.exc_info()[1]
                self.error(str(err))
        else:
            namespace, args = self._parse_known_args(args, namespace)

        if hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
            args.extend(getattr(namespace, _UNRECOGNIZED_ARGS_ATTR))
            delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)
        return namespace, args
