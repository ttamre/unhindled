from django import template
from . .models import User
from . .connect import foreign_get_author

register = template.Library()

@register.simple_tag
def getDisplayName(authorId):
    if "/" in authorId:
        #foreign
        author = foreign_get_author(authorId)
        if "displayName" in author:
            return author["displayName"]
        else: 
            return authorId
    else:
        #local
        try:
            displayName = User.objects.get(id=authorId).displayName
            return displayName
        except:
            return authorId

@register.filter(name='follow_check')
def follow_check(follower_user): 
    follower, user = follower_user.split(" ")
    return follower == user
    
@register.filter(name='addstr')
def addstr(a, b):
     return str(a)+str(b)
