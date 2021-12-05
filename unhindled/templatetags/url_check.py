from django import template
from django.core.validators import URLValidator

register = template.Library()

@register.simple_tag
def valid_url_profile(string):
  if 'https://' in str(string):
    string = string.split('/')
    if string[-1] == "":
      string.pop()
    return string[-1]
  elif 'http://' in str(string):
    string = string.split('/')
    if string[-1] == "":
      string.pop()
    return string[-1]
  else:
    return string