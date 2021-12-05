from django import template
from . .models import Comment, Post, Like
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

register = template.Library()

User = get_user_model()
 
@register.filter(name='comment_liked')
def comment_liked(comment, author):
    if str(comment).startswith('http'):
        return False
    else:
        comment = Comment.objects.get(id=comment)
        likes = Like.objects.filter(comment=comment, author=author)
        return len(likes) == 1

@register.simple_tag
def comment_text(comment, author):
    if str(comment).startswith('http'):
        return 'A'
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
def singular_like_comment(comment):
    # if 'https://' in str(post):
    #     post = post.split('/')[-1]
    #     post = uuid.UUID(post)
    # elif 'http://' in str(post):
    #     post = post.split('/')[-1]
    #     post = uuid.UUID(post)
    likes = ""
    if type(comment) != dict:
        likes = Comment.objects.filter(comment=comment)
    else:
        pass

    if len(likes) == 1:
        return "like"
    else:
        return "likes"