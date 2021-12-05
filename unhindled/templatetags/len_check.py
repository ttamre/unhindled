from django import template

register = template.Library()

@register.simple_tag
def has_content(string):
  if len(string) != 0:
    return True
  else:
    return False