import markdown
from markdown import Markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree
from markdown.extensions import Extension
from operator import attrgetter
from ..app import App
from .parse_attributes import parse_attributes
from ..utils import is_boolean_true

class SliderPattern(InlineProcessor):

  # group(1): var_name
  # group(2): var_id
  # group(3): attributes
  _PATTERN = r"\[(?:TaIpY([a-zA-Z][a-zA-Z_$0-9]*)\{(\d+)\})?slider\s*(?:\:\s*(.*?))?\s*\]"

  @staticmethod
  def extendMarkdown(md):
    md.inlinePatterns['taipy-slider'] = SliderPattern(SliderPattern._PATTERN, md)

  # TODO: Attributes:
  #   min=<value>
  #   max=<value>
  #   continous=<true/false>
  #   on_update=<func>
  def handleMatch(self, m, data):
    """Handle the match."""

    value = 0
    var_name = m.group(1)
    var_id = m.group(2)
    if var_name:
      try:
        App._get_instance().bind_var(var_name.split(sep=".")[0])
        value = attrgetter(var_name)(App._get_instance()._values)
      except:
        pass

    attributes = parse_attributes(m.group(3))
    el = etree.Element('Input')
    el.set('class', 'taipy-slider ' +  App._get_instance()._config.style_config["slider"])
    if var_name:
      el.set('key', var_name + '_' + str(var_id))
      el.set('tp_varname', var_name)
      el.set('tp_' + var_name.replace('.', '__'), '{!' + var_name.replace('.', '__') + '!}')
    el.set('type', 'range')
    el.set('value', str(value))
    el.set('min', '1')   # TODO: customize
    el.set('max', '100') # TODO: customize
    # TODO: or oninput (continuous updates)
    continuous = attributes and 'continous' in attributes and is_boolean_true(attributes['continous'])
    el.set('oninput' if continuous else 'onchange', 'onUpdate(this.id, this.value)')

    return el, m.start(0), m.end(0)
