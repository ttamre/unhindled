from django import template
from . .models import Comment, Post, Like
from django.contrib.auth.models import User
import uuid

register = template.Library()
 
@register.filter(name='post_liked')
def post_liked(post, author):
    likes = Like.objects.filter(post=post, author=author)
    return len(likes) == 1

@register.simple_tag
def post_text(post, author):
    likes = Like.objects.filter(post=post, author=author)
    if len(likes) == 1:
        return "Unlike"
    else:
        return "Like"

@register.simple_tag
def like_count_post(post):
    if 'https://' in str(post):
        post = post.split('/')[-1]
        post = uuid.UUID(post)
    elif 'http://' in str(post):
        post = post.split('/')[-1]
        post = uuid.UUID(post)

    likes = Like.objects.filter(post=post)
    return len(likes)

@register.simple_tag
def singular_like(post):
    if 'https://' in str(post):
        post = post.split('/')[-1]
        post = uuid.UUID(post)
    elif 'http://' in str(post):
        post = post.split('/')[-1]
        post = uuid.UUID(post)

    likes = Like.objects.filter(post=post)
    if len(likes) == 1:
        return "like"
    else:
        return "likes"