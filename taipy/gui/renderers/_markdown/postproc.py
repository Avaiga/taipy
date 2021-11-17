from markdown.treeprocessors import Treeprocessor

from ..builder import Builder


class Postprocessor(Treeprocessor):
    def run(self, root):
        MD_PARA_CLASSNAME = "md-para"
        for p in root.iter():
            attribs = p.attrib
            if p.tag == "p":
                classes = attribs.get("class")
                classes = MD_PARA_CLASSNAME + " " + classes if classes else MD_PARA_CLASSNAME
                attribs["class"] = classes
                p.tag = "div"
            if p != root:
                attribs["key"] = Builder._get_key(p.tag)
        return root
