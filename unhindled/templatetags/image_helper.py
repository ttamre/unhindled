from django import template

register = template.Library()
@register.simple_tag
def image_exists(image):
  if image == "":
    return "/media/upload/profile_photos/default.png"
  else:
    return image

@register.simple_tag
def image_type(contentType):
  if ("image" in contentType) or ("img" in contentType):
    return True
  return False

@register.simple_tag
def get_image_encoding(contentType, content):
  if content.startswith("data") or content.startswith("http"):
    return content
  else:
    encoding = contentType.split("/")[-1]
    data = "data:image/" + encoding + ";base64," + content
    return data