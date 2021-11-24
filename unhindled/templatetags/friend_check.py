from django import template
from . .models import Follower

register = template.Library()
 
@register.filter(name='friend_check')
def friend_check(author, user): 
    #user is the author
    if author == user:
    	return True
    #user is follows the author
    for follow in Follower.objects.filter(follower=user):
        if follow.author == author:
            return True
    return False
