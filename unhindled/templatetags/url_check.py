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

@register.simple_tag
def shorten_source(url):
  split_url = url.split(".com/")
  if len(split_url[-1]) > 0:
    return split_url[0] + ".com/"
  else:
    return url