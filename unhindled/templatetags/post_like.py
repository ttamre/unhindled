from django import template

from unhindled.connect import get_likes_on_post
from . .models import Comment, Post, Like
from django.contrib.auth.models import User
import uuid

register = template.Library()
 
@register.filter(name='post_liked')
def post_liked(post, author):
    if type(post) != dict:
        likes = Like.objects.filter(post=post, author=author)
        return len(likes) == 1
    else:
        author_id = str(author.id)
        likes = get_likes_on_post(post)
        if likes == "":
            return False
        try:
            if type(likes) == list:
                for like in likes:
                    author = like["author"]
                    if "unhindled.herokuapp.com" in author["id"]:
                        if author.id in author["id"]:
                            return True
            else:
                for like in likes["items"]:
                    author = like["author"]
                    if "unhindled.herokuapp.com" in author["id"]:
                        if author.id in author["id"]:
                            return True
        except:
            return False

    return False

@register.simple_tag
def post_text(post, author):
    if type(post) != dict:
        likes = Like.objects.filter(post=post, author=author)
    else:
        author_id = str(author.id)
        likes = get_likes_on_post(post)
        if likes == "":
            return "Like"
        try:
            if type(likes) == list:
                for like in likes:
                    author = like["author"]
                    if "unhindled.herokuapp.com" in author["id"]:
                        if author.id in author["id"]:
                            return "Unlike"
            else:
                for like in likes["items"]:
                    author = like["author"]
                    if "unhindled.herokuapp.com" in author["id"]:
                        if author.id in author["id"]:
                            return "Unlike"
        except:
            return "Like"

    if len(likes) == 1:
        return "Unlike"
    else:
        return "Like"

@register.simple_tag
def like_count_post(post):


    likes = ""
    if type(post) != dict:
        likes = Like.objects.filter(post=post)
    else:
        likes_json = get_likes_on_post(post)
        if likes_json != "":
            if type(likes_json) == list:
                likes = likes_json
            elif "items" in likes_json.keys():
                likes = likes_json["items"]
            
    return len(likes)

@register.simple_tag
def singular_like(post):
    
    likes = ""
    if type(post) != dict:
        likes = Like.objects.filter(post=post)
    else:
        likes_json = get_likes_on_post(post)
        if likes_json != "":

            if type(likes_json) == list:
                likes = likes_json

            elif "items" in likes_json.keys():
                likes = likes_json["items"]

    if len(likes) == 1:
        return "like"
    else:
        return "likes"