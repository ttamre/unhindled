from django import template
from django.db.models.query import QuerySet

from unhindled.connect import get_comment_likes
from . .models import Comment, Post, Like
from django.contrib.auth import get_user_model

register = template.Library()

User = get_user_model()

@register.simple_tag
def get_likes(comment, post):
    if type(post) == dict:
        likes = get_comment_likes(comment["id"], post)
        return likes
    else:
        return Like.objects.filter(comment=comment)

@register.simple_tag
def likes_count(like_list):
    return len(like_list)

@register.simple_tag
def comment_liked(like_list, author):
    if type(like_list) == QuerySet:
        likes = like_list.filter(author=author)
        return len(likes) == 1
    else:
        for like in like_list:
            id = str(author.id)
            if id in like["author"]["id"]:
                return True
            else:
                return False


@register.simple_tag
def comment_text(comment, author):
    if str(comment).startswith('http'):
        return 'Like'
    else:
        comment = Comment.objects.get(id=comment)
        likes = Like.objects.filter(comment=comment, author=author)
        if len(likes) >= 1:
            return "Unlike"
        else:
            return "Like"

@register.simple_tag
def like_count_comment(comment):
    if str(comment).startswith('http'):
        return 0
    else:
        comment = Comment.objects.get(id=comment)
        likes = Like.objects.filter(comment=comment)
        return len(likes)

@register.simple_tag
def singular_like_comment(likes_list):
    
    if len(likes_list) == 1:
        return "Like"
    else:
        return "Likes"