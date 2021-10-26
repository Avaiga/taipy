from markdown.treeprocessors import Treeprocessor

class Postprocessor(Treeprocessor):

    def run(self, root):
        MD_PARA_CLASSNAME = "md-para"
        for p in root.iter("p"):
          attribs = p.attrib
          classes = attribs.get("class")
          if classes:
            classes = MD_PARA_CLASSNAME + " " + classes
          else:
            classes = MD_PARA_CLASSNAME
          attribs["class"] = classes
          p.tag = "div"
        return root

