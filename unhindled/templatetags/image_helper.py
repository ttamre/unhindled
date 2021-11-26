from django import template

register = template.Library()
@register.simple_tag
def image_exists(image):
  if image == "":
    return "/media/upload/profile_photos/default.png"
  else:
    return image