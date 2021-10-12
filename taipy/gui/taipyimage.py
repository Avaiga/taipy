import typing as t


class TaipyImage:
    @staticmethod
    def get_dict_or(value: t.Union[str, t.Any]) -> t.Union[str, dict]:
        return value if isinstance(value, str) else value.to_dict()

    def __init__(self, path: str, text: t.Optional[str] = None) -> None:
        self.path = path
        self.text = text
        pass

    def to_dict(self, a_dict: t.Optional[dict] = None) -> dict:
        if a_dict is None:
            a_dict = {}
        a_dict["path"] = self.path
        if self.text is not None:
            a_dict["text"] = self.text
        return a_dict
