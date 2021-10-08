import typing as t


class Partial(object):

    __partials = {}

    def __init__(self, markdown: t.Optional[str] = None, markdown_file: t.Optional[str] = None):
        self.index_html = None
        self.md_template = markdown
        self.md_template_file = markdown_file
        self.style = None
        self.route = "/partials/tp_" + str(len(Partial.__partials))
        Partial.__partials[self.route] = self
