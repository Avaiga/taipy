import typing as t


class Icon:
    """Small image in the User Interface.

    Icons are typically used in controls like [button](../gui/viselements/button.md)
    or items in a [menu](../gui/viselements/menu.md).

    Attributes:
        path (str): the path to the image file.
        text (Optional[str]): the text associated to the image or None if there is none.

    If a text is associated to an icon, it is rendered by the visual elements that
    uses this Icon.
    """

    @staticmethod
    def get_dict_or(value: t.Union[str, t.Any]) -> t.Union[str, dict]:
        return value._to_dict() if isinstance(value, Icon) else value

    def __init__(self, path: str, text: t.Optional[str] = None) -> None:
        """Initialize a new Icon.

        Arguments:
            path: the path to an image file.
            text: the text associated to the image. If _text_ is None, there is no text
                associated to this image.
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
