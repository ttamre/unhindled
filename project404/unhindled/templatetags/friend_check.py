from django import template
from . .models import Friendship

register = template.Library()
 
@register.filter(name='friend_check')
def friend_check(author, user): 
    #user is the author
    if author == user:
    	return True
    #user is friends with the author or follows them
    for friendship in Friendship.objects.filter(requesterId=user):
        if friendship.adresseeId == author:
            return True
    #user is friends with the author, not the author follows the user
    for friendship in Friendship.objects.filter(adresseeId=user):
        if friendship.requesterId == author and friendship.status == "accepted":
            return True
    return False
