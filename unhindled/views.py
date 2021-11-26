from django.contrib.auth import login
from django.db import reset_queries
from django.shortcuts import get_object_or_404, render, redirect
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Like, Post, Follower, FollowRequest, UserProfile, Comment
from requests.models import Response as MyResponse
from rest_framework.response import Response
from .forms import *
from .connect import *
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import viewsets
from .serializers import *
from rest_framework import serializers

import requests
import json
import os
import datetime, math
import sys
import socket
from itertools import chain

from django.core import serializers as core_serializers

from unhindled import serializers
from .connect import *

User = get_user_model()

CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
GITHUB_AUTH = (CLIENT_ID, CLIENT_SECRET)

GITHUB_EVENTS = {
    "CreateEvent": "Created repository",
    "PushEvent":   "Pushed code",
    "PullEvent":   "Pulled code",
    "ForkEvent":   "Forked repo",
    "MemberEvent": "Managed organization",
    "PullRequestEvent": "Pull request",
    None: "Unknown event"
}
#get id for apis given user
def getForeignId(user):
    return "https://unhindled.herokuapp.com/" + "author/" + str(user.id)
def paginationGetter(page, size):
    try:
        size = int(size)
        if size <= 0:
            size = 5
    except:
        size = 5

    try:
        page = int(page)
        if page <=0:
            page = 1
    except:
        page = 1

    return page, size

# Create your views here.
class HomeView(generic.ListView):
    model = Post
    template_name = "unhindled/index.html"
    ordering = ['-published']
    # paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        original = context['object_list']
        context['object_list'] = chain(get_foreign_posts_list(), original)
        return context

class SignUpView(generic.CreateView):
    form_class = CreateUserForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class PostViewSet(viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all().order_by('published')
    serializer_class = PostSerializer

    def list(self, request, user_id):
        user = User.objects.get(user_id=user_id)
        queryset = Post.objects.filter(author=user).order_by('published')
        serializer = PostSerializer(queryset, many=True)

        page = request.GET.get("page",1)
        size = request.GET.get("size",5)

        page, size = paginationGetter(page, size)

        postData = serializer.data[((page-1)*size):page*size]

        data = {}
        data["type"] = "posts"
        data["page"] = page
        data["size"] = math.ceil(len(serializer.data) / size)
        data["items"] = postData

        return Response(data)

    def retrieve(self, request, user_id, post_id):
        user = User.objects.get(user_id=user_id)
        try:
            queryset = Post.objects.get(id=post_id)
        except:
            return Response({}, status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(queryset)
        return Response(serializer.data)

    def allPosts(self, request):
        posts = Post.objects.filter(visibility='PUBLIC').order_by('published')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def createPost(self, request, user_id,post_id=None):
        if post_id != None:
            post = Post.objects.filter(id=post_id)
            if len(post) > 0:
                return Response({"Error":"Post id already exists"}, status=status.HTTP_400_BAD_REQUEST)

        loggedInUser = request.user
        user = User.objects.get(user_id=user_id)

        if user != loggedInUser:
            return Response({"author":"Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)

        postData = request.POST
        author = user
        contentType = 'txt'
        for types in Post.CONTENT_TYPES:
            if types[1] == postData["contentType"] or types[0] == postData["contentType"]:
                contentType = types[0]

        
        title = postData.get("title",None)
        description = postData.get("description",None)

        visibility = 'PUBLIC'
        for types in Post.VISIBILITY:
            if types[1].lower() == postData["visibility"].lower():
                visibility = types[0]

        send_to = None
        if ("sent_to" in postData.keys()):
            if (postData["sent_to"] is not None) and postData["sent_to"] != "":
                try:
                    send_to = User.objects.get(user_id=user_id)
                except:
                    send_to = User.objects.get(pk=postData["sent_to"])

        published = datetime.datetime.now()
        if ("published") in postData.keys():
            if (postData["published"] is not None) and postData["published"] != "":
                published = datetime.datetime(postData["published"])
        #will need to change
        content = postData.get("content",None)
        images = postData.get("images",None)

        try:
            newPost = Post(author=author,title=title,description=description,visibility=visibility,send_to=send_to,published=published,
                            content=content,contentType=contentType,images=images)
            if post_id != None:
                newPost.id = post_id

            newPost.save()
            serializer = PostSerializer(newPost)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    def updatePost(self, request, user_id, pk):
        loggedInUser = request.user
        user = User.objects.get(user_id=user_id)
        try:
            postToEdit = Post.objects.get(id=pk)
        except:
            return Response({}, status.HTTP_404_NOT_FOUND)
            
        if user != loggedInUser:
            return Response({"author":"Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)

        postData = request.POST
        warning = {}
        if "contentType" in postData.keys():
            if postData["contentType"] != "":
                for types in Post.CONTENT_TYPES:
                    if types[1] == postData["contentType"] or types[0] == postData["contentType"]:
                        postToEdit.contentType = types[0]
        if "title" in postData.keys() and postData["title"] != "":
            if postData["contentType"] != "":
                postToEdit.title = postData["title"]
        if "description" in postData.keys() and postData["description"] != "":
            postToEdit.description = postData["description"]
        if "content" in postData.keys() and postData["content"] != "":
            postToEdit.content = postData["content"]
        if "visibility" in postData.keys() and postData["visibility"] != "":
            for types in Post.VISIBILITY:
                if types[1].lower() == postData["visibility"].lower():
                    if types[0] != "send":
                        postToEdit.visibility = types[0]
                    else:
                        warning["visibility"] =  "Post can't be converted to a Inbox post, please delete the post and repost with changed visibility"
        if "send_to" in postData.keys() and postData["send_to"] != "":
            warning["send_to"] =  "Post can't change receiver. Please delete post and resend"
        if "published" in postData.keys() and postData["published"] != "":
            warning["published"] = "Published date can't be changed"
        if "images" in postData.keys() and postData["images"] != "":
            postToEdit.images = postData["images"]
    
        try:
            postToEdit.save()
            serializer = PostSerializer(postToEdit)
            data = {}
            data["UpdatedPost"] = serializer.data
            if len(warning.keys()) > 0:
                data["Warnings"] = warning
            return Response(data, status=status.HTTP_202_ACCEPTED)

        except:
            errors = {}
            errors["Error"] = "Invalid post format"
            errors["ReceivedData"] = postData
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def deletePost(self, request, user_id, pk):
        loggedInUser = request.user
        user = User.objects.get(user_id=user_id)
        try:
            postToDelete = Post.objects.get(id=pk)
        except:
            return Response({}, status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(postToDelete)
        if user != loggedInUser:
            return Response({"author":"Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)

        postToDelete.delete()
        return Response({"deleted_post": serializer.data}, status=status.HTTP_202_ACCEPTED)

class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)

        page = request.GET.get("page",1)
        size = request.GET.get("size",5)
        page, size = paginationGetter(page, size)

        userData = serializer.data[((page-1)*size):page*size]

        data = {}
        data["type"] = "authors"
        data["page"] = page
        data["size"] = math.ceil(len(serializer.data) / size)
        data["items"] = userData
        return Response(data)

    def retrieve(self, request, id):
        queryset = UserProfile.objects.all()
        try:
            user = User.objects.get(user_id=id)
        except:
            try:
                user = User.objects.get(pk=int(id))
            except:
                return Response({"Error": "User not found"}, status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def authorUpdate(self, request, id):
        try:
            user = User.objects.get(user_id=id)
        except:
            try:
                user = User.objects.get(pk=int(id))
            except:
                return Response({"Error": "User not found"}, status.HTTP_404_NOT_FOUND)

        loggedInUser = request.user
        if user != loggedInUser:
            return Response({"author":"Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)

        userProfile = UserProfile.objects.get(user=user)
        
        updateData = request.POST

        if "user_id" in updateData.keys() and updateData["user_id"] != "":
            otherUser = User.objects.filter(user_id=updateData["user_id"])
            if len(otherUser) > 0:
                return Response({"error": "user_id already exists"}, status=status.HTTP_400_BAD_REQUEST)
            user.user_id = updateData["user_id"]
        if "first_name" in updateData.keys() and updateData["first_name"] != "":
            user.first_name = updateData["first_name"]
        if "last_name" in updateData.keys() and updateData["last_name"] != "":
            user.last_name = updateData["last_name"]
        if "email" in updateData.keys() and updateData["email"] != "":
            user.email = updateData["email"]
        if "displayName" in updateData.keys() and updateData["displayName"] != "":
            userProfile.displayName = updateData["displayName"]
        if "github" in updateData.keys() and updateData["github"] != "":
            userProfile.github = updateData["github"]
        if "profileImage" in updateData.keys() and updateData["profileImage"] != "":
            userProfile.profileImage = updateData["profileImage"]

        try:
            user.save()
            userProfile.save()
            serializer = UserSerializer(user)
            data = {}
            data["UpdatedUser"] = serializer.data
            return Response(data, status=status.HTTP_202_ACCEPTED)

        except:
            errors = {}
            errors["Error"] = "Invalid post format" 
            errors["ReceivedData"] = updateData
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all().order_by('published')
    serializer_class = CommentSerializer

    def list(self, request, user_id, post_id):
        user = User.objects.get(user_id=user_id)
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        page = request.GET.get("page",1)
        size = request.GET.get("size",5)
        page, size = paginationGetter(page, size)

        commentData = serializer.data[((page-1)*size):page*size]

        host = "https://unhindled.herokuapp.com/"
        data = {}
        data["type"] = "comments"
        data["page"] = page
        data["size"] = math.ceil(len(serializer.data) / size)
        data["post"] = host + post.author.user_id + "/posts/" + str(post.id) + "/comments"
        data["comments"] = commentData
        return Response(data)

    def retrieve(self, request, user_id, post_id, comment_id):
        user = User.objects.get(user_id=user_id)
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.get(id=comment_id)
        serializer = CommentSerializer(comments)
        return Response(serializer.data)

    def postComment(self, request, user_id, post_id):
        loggedInUser = request.user
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response({"error": "post not found"}, status.HTTP_404_NOT_FOUND)

        if loggedInUser.is_authenticated:
            commentData = request.POST
            if ("comment" not in commentData.keys()) or ("contentType" not in commentData.keys()):
                return Response({"error": "missing comment text or contentType"}, status.HTTP_400_BAD_REQUEST)

            if commentData["contentType"] not in ["md", "txt"]:
                return Response({"error": "comment only supports md and txt"}, status.HTTP_400_BAD_REQUEST)

            try:
                newComment = Comment(post=post,author=loggedInUser,
                    comment=commentData["comment"],contentType=commentData["contentType"])

                newComment.save()

                serializer = CommentSerializer(newComment)
                return Response({"NewComment": serializer.data}, status.HTTP_201_CREATED)

            except:
                return Response({"error": "Could not save comment"}, status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"author":"Need to login"}, status=status.HTTP_401_UNAUTHORIZED)

class FollowerListViewset (viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self, request, author):
        authorObj = get_object_or_404(User, user_id=author)
        user = Follower.objects.filter(author=authorObj)
        serializer = FollowerListSerializer(user, many=True)
        return Response(serializer.data)
    
class FollowerViewset (viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, author, follower):
        authorObj = get_object_or_404(User, username=author)
        follow = get_object_or_404(Follower, author=authorObj, follower=follower)
        serializer = FollowerSerializer(follow)
        return Response(serializer.data)
    def update(self, request, author, follower):
        authorObj = get_object_or_404(User, username=author)
        Follower.objects.create(author=authorObj, follower=follower)
        follow = get_object_or_404(Follower, author=author, follower=follower)
        serializer = FollowerSerializer(follow)
        return Response(serializer.data)
    def destroy(self, request, author, follower):
        authorObj = get_object_or_404(User, username=author)
        follow = get_object_or_404(Follower, author=authorObj, follower=follower)
        serializer = FollowerSerializer(follow)
        follow.delete()
        return Response(serializer.data)

class FriendRequestViewset (viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self, request, author, follower):
        authorObj = get_object_or_404(User, id=author)
        followerObj = get_object_or_404(User, id=follower)
        FollowRequest.objects.create(author=authorObj, follower=followerObj)
        followRequest = get_object_or_404(Follower, author=author, follower=follower)
        serializer = FollowerRequestSerializer(followRequest)
        return Response(serializer.data)

class LikeViewSet(viewsets.ViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def commentList(self, request, user_id, post_id, comment_id):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }
        comment = Comment.objects.get(id=comment_id)
        likes = Like.objects.filter(comment=comment)
        serializer = LikeSerializer(likes, many=True, context=serializer_context)

        likeData = serializer.data
        data = {}
        data["type"] = "likes"
        data["items"] = likeData
        return Response(data)

    def postList(self, request, user_id, post_id):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }
        post = Post.objects.get(id=post_id)
        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True, context=serializer_context)

        likeData = serializer.data
        data = {}
        data["type"] = "likes"
        data["items"] = likeData
        return Response(data)

    def authorList(self, request, user_id):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }

        author = User.objects.get(user_id=user_id)
        likes = Like.objects.filter(author=author)
        serializer = LikeSerializer(likes, many=True, context=serializer_context)

        likeData = serializer.data
        for like in likeData:
            del like["author"]
        data = {}
        data["type"] = "liked"
        data["items"] = likeData
        return Response(data)

    def likePost(self, request, user_id, post_id):
        loggedInUser = request.user
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response({"error": "post not found"}, status.HTTP_404_NOT_FOUND)

        if loggedInUser.is_authenticated:
            try:
                existingLike = Like.objects.filter(post=post,author=loggedInUser)
                if len(existingLike) > 0:
                    serializer = LikeSerializer(existingLike,many=True)
                    data = {}
                    data["unlikedPost"] = serializer.data
                    existingLike.delete()
                    
                    return Response(data, status.HTTP_202_ACCEPTED)

                newLike = Like(post=post,author=loggedInUser)
                newLike.save()

                serializer = LikeSerializer(newLike)
                return Response({"likedPost": serializer.data}, status.HTTP_201_CREATED)

            except:
                return Response({"error": "Could not like/unlike post"}, status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"author":"Need to login"}, status=status.HTTP_401_UNAUTHORIZED)

    def likeComment(self, request, user_id, post_id, comment_id):
        loggedInUser = request.user
        try:
            comment = Comment.objects.get(id=comment_id)
        except:
            return Response({"error": "post not found"}, status.HTTP_404_NOT_FOUND)

        if loggedInUser.is_authenticated:
            try:
                existingLike = Like.objects.filter(comment=comment,author=loggedInUser)
                if len(existingLike) > 0:
                    serializer = LikeSerializer(existingLike, many=True)
                    data = {}
                    data["unlikedComment"] = serializer.data
                    existingLike.delete()
                    
                    return Response(data, status.HTTP_202_ACCEPTED)

                newLike = Like(comment=comment,author=loggedInUser)
                newLike.save()

                serializer = LikeSerializer(newLike)
                return Response({"likedComment": serializer.data}, status.HTTP_201_CREATED)

            except:
                return Response({"error": "Could not like/unlike comment"}, status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"author":"Need to login"}, status=status.HTTP_401_UNAUTHORIZED)

class StreamView(generic.ListView):
    model = Post
    template_name = "unhindled/mystream.html"
    ordering = ['-published']

    def get(self, request, *args, **kwargs):
        response = requests.get(f'https://api.github.com/users/{request.user}/events/PUBLIC', auth=GITHUB_AUTH)
        events = response.json()
        event_list = []

        if response.ok:
            for event in events:
                repo = event.get("repo", {}).get("name")
                type_ = GITHUB_EVENTS.get(event.get("type"))

                repo_api = event.get("repo", {}).get("url")
                repo_resp = requests.get(repo_api, auth=GITHUB_AUTH)
                
                # Public repos
                if repo_resp.ok:
                    url = repo_resp.json().get("html_url")

                # Private repos - use profile URL instead
                else:
                    user_api = event.get("actor", {}).get("url")
                    user_resp = requests.get(user_api, auth=GITHUB_AUTH)
                    if user_resp.ok:
                        url = user_resp.json().get("html_url")
                    else:
                        url = None

                event_list.append({"repo": repo, "type": type_, "url": url,})

        return render(request, 'unhindled/mystream.html', {"event_list": event_list})


class AccountView(generic.CreateView):
    model = User
    template_name = "unhindled/account.html"
    fields = "__all__"


class ManageFriendView(generic.ListView):
    model = Follower
    template_name = "unhindled/friends.html"
    fields = "__all__"
    
def follow(request):
    author = request.POST["author"]
    #internal user
    if User.objects.filter(username=author).count() == 1:
       authorId = User.objects.get(username=author).id
       if Follower.objects.filter(author=authorId,follower=request.user.id).count() == 0:
           Follower.objects.create(author=authorId, follower=request.user.id)
           if Follower.objects.filter(author=request.user.id,follower=authorId).count() == 0 and FollowRequest.objects.filter(author=request.user.id,follower=authorId).count() == 0:
                FollowRequest.objects.create(author=request.user.id, follower=authorId)
    #foreign user
    else:
        foreignAuthors = get_foreign_authors_list()
        for foreignAuthor in foreignAuthors:
            if foreignAuthor['displayName'] == author:
                authorId = foreignAuthor['id']
                if Follower.objects.filter(author=authorId,follower=request.user.id).count() == 0 :
                    Follower.objects.create(author=authorId, follower=request.user.id)
                    z = getForeignId(request.user)
                    x = foreign_add_follower(authorId, z)
                    y = x["fr"]
           ### will need to send friend request here ###
                    break
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

def deleteFollowRequest(request):
    followRequest = FollowRequest.objects.get(author=request.POST["author"],follower=request.user.user_id)
    follow.delete()
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)    

def unfollow(request):
    author = request.POST["author"]
    follow = Follower.objects.get(author=author,follower=request.user.id)
    follow.delete()
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)


class CreatePostView(generic.CreateView):
    model = Post
    template_name = "unhindled/create_post.html"
    fields = "__all__"

# def SharePost(request, user, post_id):
#     return HttpResponseRedirect(reverse('index'))


class SharePost(generic.View):
    def get(self, request, user, id):
        post_object = get_object_or_404(Post, pk=id)
        current_user = request.user
        if current_user == User:
            return HttpResponseRedirect(reverse('viewPost', args=(str(current_user ), post_object.id)))

        if post_object.is_shared_post:
            post_object = post_object.originalPost

        sharedPost = Post.objects.create(author=post_object.author, contentType=post_object.contentType,
        title=post_object.title, description=post_object.description,
        visibility=post_object.visibility, published=post_object.published, content=post_object.content,
        images=post_object.images, originalPost=post_object, sharedBy=current_user).save()
        return HttpResponseRedirect(reverse('index'))
  
def likeObject(request, user_id, id, obj_type):
    author = User.objects.get(id=user_id)
    if obj_type == "comment":
        comment = Comment.objects.get(id = id)
        existingLike = Like.objects.filter(comment=comment,author=author)
        if (len(existingLike) == 0):
            like = Like(comment=comment,author=author)
            like.save()
        post = comment.post
    elif obj_type == "post":
        post = Post.objects.get(id = id)
        existingLike = Like.objects.filter(post=post,author=author)
        if (len(existingLike) == 0):
            like = Like(post=post,author=author)
            like.save()

    return HttpResponseRedirect(post.get_absolute_url())

def unlikeObject(request, user_id, id, obj_type):
    author = User.objects.get(id=user_id)
    if obj_type == "comment":
        comment = Comment.objects.get(id = id)
        existingLike = Like.objects.filter(comment=comment,author=author)
        if (len(existingLike) >= 1):
            existingLike.delete()
        post = comment.post
    elif obj_type == "post":
        post = Post.objects.get(id = id)
        existingLike = Like.objects.filter(post=post,author=author)
        if (len(existingLike) >= 1):
            existingLike.delete()

    return HttpResponseRedirect(post.get_absolute_url())


def view_post(request, user_id, id):
    try:
        post = get_object_or_404(Post, id=id)
    except:
        post = get_json_post(id)

    if type(post) is dict:
        post_id = post['id'].split('/post')[-1]
        post_id = uuid.UUID(post_id.split('s/')[-1])
        comments = Comment.objects.filter(post=post_id).order_by('-published')
        if request.method == 'POST':
            form_comment = FormComment(request.POST or None)
            if form_comment.is_valid():
                comment = request.POST.get('comment')
                comm = Comment.objects.create(post=post, author=request.user, comment=comment)
                comm.save()
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            form_comment= FormComment()
    else:
        comments = Comment.objects.filter(post=post).order_by('-published')
        if request.method == 'POST':
            form_comment = FormComment(request.POST or None)
            if form_comment.is_valid():
                comment = request.POST.get('comment')
                comm = Comment.objects.create(post=post, author=request.user, comment=comment)
                comm.save()
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            form_comment= FormComment()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': form_comment
    }
    return render(request, 'unhindled/view_post.html', context)


class UpdatePostView(generic.UpdateView):
    model = Post
    template_name = "unhindled/edit_post.html"
    fields = "__all__"

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            return super(UpdatePostView, self).post(request, *args, **kwargs)


class DeletePostView(generic.DeleteView):
    model = Post
    template_name = "unhindled/delete_post.html"
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            return super(DeletePostView, self).post(request, *args, **kwargs)


class ProfileView(View):
    def get(self, request, id, *args, **kwargs):
        profile = UserProfile.objects.get(pk=id)
        user = profile.user
        user_post = Post.objects.filter(author=user).order_by('-published')

        context = {
            'user': user,
            'profile': profile,
            'posts': user_post,
        }
        return render(request, 'unhindled/profile.html', context)


class EditProfileView(generic.UpdateView):
    model = UserProfile
    fields = ['displayName', 'date_of_birth',  'location', 'github', 'more_info'] #'profileImage' removing profileImage for now b/c clearing image breaks the site
    template_name = 'unhindled/edit_profile.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user



@api_view(['GET'])
# @authentication_classes([CustomAuthentication])
def get_foreign_posts(request):
    if request.method == "GET":
        foreign_posts = get_foreign_posts_list()
        return Response({"foreign posts": foreign_posts})
    else:
        return Response({"message": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
# @authentication_classes([CustomAuthentication])
def get_foreign_authors(request):
    if request.method == "GET":
        foreign_authors = get_foreign_authors_list()
        return Response({"foreign authors": foreign_authors})
    else:
        return Response({"message": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
