
import os
import typing as t


def get_style(style: t.Union[str, t.Dict[str, t.Union[str, t.Dict[str, t.Any]]]]):
    """NOT DOCUMENTED"""
    if isinstance(style, dict):
            style_arr = []
            for k, v in style.items():
                if isinstance(v, dict):
                    rules= []
                    for vk, vv in v.items():
                        if isinstance(vv, dict):
                             rules.append(get_style({vk: vv}))
                        else:
                            rules.append(f'{vk}:{vv};')
                    if rules:
                        style_arr.append(f"{k}{{{''.join(rules)}}}")
            return os.linesep.join(style_arr) if style_arr else None
    return style
