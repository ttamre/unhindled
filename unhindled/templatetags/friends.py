from django import template
from . .models import User
from . .connect import foreign_get_author

register = template.Library()

@register.simple_tag
def getDisplayName(authorId):
    if "/" in authorId:
        #foreign
        author = foreign_get_author(authorId)
        return author["displayName"]
    else:
        #local
        author = User.objects.get(id=authorId).displayName
        
