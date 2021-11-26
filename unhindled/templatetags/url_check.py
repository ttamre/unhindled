from django import template
from django.core.validators import URLValidator

register = template.Library()

@register.simple_tag
def valid_url_profile(string):
  if 'https://' in str(string):
    return string
  else:
    url = 'https://unhindled.herokuapp.com/' + str(string) + '/author'
    return url
