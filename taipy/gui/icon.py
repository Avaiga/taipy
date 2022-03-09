import typing as t


class Icon:
    """This class allows to manage Images in Gui.

    Attributes:

        path (str): Path to an image file.
        text (optional(str)): Text associated to the image
    """

    @staticmethod
    def get_dict_or(value: t.Union[str, t.Any]) -> t.Union[str, dict]:
        return value._to_dict() if isinstance(value, Icon) else value

    def __init__(self, path: str, text: t.Optional[str] = None) -> None:
        """Icon constructor.

        Args:

            path (str): Path to an image file.
            text (optional(str)): Text associated to the image
        """
        self.path = path
        self.text = text

    def _to_dict(self, a_dict: t.Optional[dict] = None) -> dict:
        if a_dict is None:
            a_dict = {}
        a_dict["path"] = self.path
        if self.text is not None:
            a_dict["text"] = self.text
        return a_dict
