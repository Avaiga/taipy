import markdown
from markdown import Markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree
from markdown.extensions import Extension
from operator import attrgetter
from ..app import App
from .parse_attributes import parse_attributes

# The table pattern also handles the [<var>] construct
class TablePattern(InlineProcessor):

  # group(1): var_name
  # group(2): var_id
  # group(3): table+attributes
  # group(4): attributes
  _PATTERN = r"\[(?:TaIpY([a-zA-Z][\.a-zA-Z_$0-9]*)\{(\d+)\})?(table\s*(?:\:\s*(.*?))?)?\s*\]"

  @staticmethod
  def extendMarkdown(md):
    md.inlinePatterns['taipy-table'] = TablePattern(TablePattern._PATTERN, md)

  def handleMatch(self, m, data):
    """Handle the match."""

    value = '<empty>'
    var_name = m.group(1)
    var_id = m.group(2)
    if var_name:
        try:
            # Bind variable name (var_name string split in case var_name is a dictionary)
            App._get_instance().bind_var(var_name.split(sep=".")[0])
        except:
            print("error")

    el = etree.Element("Table")
    el.set('className', 'taipy-table ' + App._get_instance()._config.style_config["table"])
    if var_name:
        el.set('key', var_name + '_' + str(var_id))
        el.set('tp_' + var_name.replace('.', '__'), '{!' + var_name.replace('.', '__') + '!}')
        el.set('tp_varname', var_name)
    attributes = parse_attributes(m.group(4))
    page_size = (attributes and 'page_size' in attributes and attributes['page_size']) or '100'
    el.set('pageSize', '{!' + page_size + '!}')

    return el, m.start(0), m.end(0)
