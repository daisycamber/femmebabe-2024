from django.utils.html import strip_tags, escape
import six
from django.template.base import Node
from django.utils.functional import keep_lazy
from django import template
from django.shortcuts import get_object_or_404
import re

register = template.Library()

@register.tag
def linebreakless(parser, token):
    nodelist = parser.parse(('endlinebreakless',))
    parser.delete_first_token()
    return LinebreaklessNode(nodelist)

class LinebreaklessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        strip_line_breaks = keep_lazy(six.text_type)(lambda x: x.replace('\n', ''))
        return strip_line_breaks(self.nodelist.render(context).strip())
