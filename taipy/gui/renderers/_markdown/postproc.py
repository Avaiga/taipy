from markdown.treeprocessors import Treeprocessor

from ..builder import _Builder


class _Postprocessor(Treeprocessor):
    @staticmethod
    def extend(md, gui, priority):
        instance = _Postprocessor(md)
        md.treeprocessors.register(instance, "taipy", priority)
        instance._gui = gui

    def run(self, root):
        MD_PARA_CLASSNAME = "md-para"
        for p in root.iter():
            if p.tag == "p":
                classes = p.get("class")
                classes = f"{MD_PARA_CLASSNAME} {classes}" if classes else MD_PARA_CLASSNAME
                p.set("class", classes)
                p.tag = "div"
            if p != root:
                p.set("key", _Builder._get_key(p.tag))
        return root
