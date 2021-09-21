import re

from markdown.preprocessors import Preprocessor

from ..app import App


class TaipyPreprocessor(Preprocessor):
    _VAR_RE = re.compile(r"\[<\s*([a-zA-Z][\.a-zA-Z_$0-9]*)\s*>(\s*:\s*(.*?)\s*)?\]")

    def run(self, lines):
        new_lines = []
        for line in lines:
            new_line = ""
            last_index = 0
            for m in self._VAR_RE.finditer(line):
                variable_name = m.group(1)
                new_line = (
                    new_line
                    + line[last_index : m.start()]
                    + f"[TaIpY{variable_name}{{{str(App._get_instance()._add_control(variable_name))}}}"
                )
                if m.group(2):
                    new_line += m.group(3)
                new_line += "]"
                last_index = m.end()
            if last_index == 0:
                new_lines.append(line)
            else:
                new_lines.append(new_line + line[last_index:])
        return new_lines
