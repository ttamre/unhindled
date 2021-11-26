from django import template
import datetime

register = template.Library()

@register.simple_tag
def days_from_now(dt):
  today = datetime.datetime.now()
  print(type(dt))
  print(today-dt)
  return "hi"