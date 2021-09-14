import markdown
from markdown import Markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree
from markdown.extensions import Extension
from operator import attrgetter
from ..app import App
from .parse_attributes import parse_attributes

class ButtonPattern(InlineProcessor):

  # group(1): var_name
  # group(2): var_id
  # group(3): attributes
  _PATTERN = r"\[(?:TaIpY([a-zA-Z][a-zA-Z_$0-9]*)\{(\d+)\})?button\s*(?:\:\s*(.*?))?\s*\]"

  @staticmethod
  def extendMarkdown(md):
    md.inlinePatterns['taipy-button'] = ButtonPattern(ButtonPattern._PATTERN, md)

  # TODO: Attributes:
  #   on_action=<func>
  def handleMatch(self, m, data):
    """Handle the match."""
    value = '<empty>'
    var_name = m.group(1)
    var_id = m.group(2)
    if var_name:
      try:
        App._get_instance().bind_var(var_name.split(sep=".")[0])
        value = attrgetter(var_name)(App._get_instance()._values)
      except:
        value = '[Undefined: ' + var_name + ']'

    attributes = parse_attributes(m.group(3))
    el = etree.Element('Input')
    el.set('class', 'taipy-button ' + App._get_instance()._config.style_config["button"])
    if attributes and 'id' in attributes:
      el.set('id', attributes['id'])
      el.set('key', attributes['id'])
    elif var_name:
      el.set('id', var_name + '_' + str(var_id))
      el.set('key', var_name + '_' + str(var_id))
      el.set('tp_' + var_name.replace('.', '__'), '{!'+ var_name.replace('.', '__') +'!}')
      el.set('tp_varname', var_name)
    if attributes and 'on_action' in attributes:
      # el.set('onclick', 'onAction(this, \'' + attributes['on_action'] + '\')')
      el.set('actionName', attributes['on_action'])
    else:
      # el.set('onclick', 'onAction(this, null)')
      el.set('actionName', '')
    el.set('type', 'button')
    el.set('value', attributes['label'] if attributes and 'label' in attributes else str(value))

    return el, m.start(0), m.end(0)
