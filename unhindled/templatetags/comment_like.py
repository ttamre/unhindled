from django import template
from . .models import Comment, Post, Like
from django.contrib.auth.models import User

register = template.Library()
 
@register.filter(name='comment_liked')
def comment_liked(comment, author):
    likes = Like.objects.filter(comment=comment, author=author)
    return len(likes) == 1

@register.simple_tag
def comment_text(comment, author):
    likes = Like.objects.filter(comment=comment, author=author)
    if len(likes) == 1:
        return "Unlike"
    else:
        return "Like"

@register.simple_tag
def like_count(comment):
    likes = Like.objects.filter(comment=comment)
    return len(likes)