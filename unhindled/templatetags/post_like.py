from django import template
from django.db.models.query import QuerySet

from unhindled.connect import get_likes_on_post
from . .models import Comment, Post, Like
from django.contrib.auth.models import User
import uuid

register = template.Library()

@register.simple_tag
def get_likes_post(post):
    if type(post) == dict:
        likes = get_likes_on_post(post)
        if likes == '':
            return "0 Likes"
        if type(likes) == dict:
            try:
                return likes["items"]
            except:
                return likes["item"]
        return likes
    else:
        likes = Like.objects.filter(post=post)
        return likes