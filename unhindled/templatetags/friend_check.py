from django import template
from . .models import Follower

register = template.Library()
 
@register.filter(name='friend_check')
def friend_check(author_user): 
    author, user = author_user.split(" ")
    #user is the author
    if author==user:
    	return True
    #user follows the author
    for follow in Follower.objects.filter(follower=user):
        if follow.author == author:
            return True
    return False
    
@register.filter(name='addstr')
def addstr(a, b):
     return str(a)+str(b)
