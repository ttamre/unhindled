from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser, User
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Like, Post, Friendship, UserProfile, Comment
from requests.models import Response as MyResponse
from rest_framework.response import Response
from .models import Post, Friendship, UserProfile, Comment
from .forms import *
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from rest_framework import viewsets

from .serializers import CommentSerializer, LikeSerializer, PostSerializer, UserSerializer

import requests
import json
import os

from unhindled import serializers

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
    ordering = ['-created_on']

class SignUpView(generic.CreateView):
    form_class = CreateUserForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class PostViewSet(viewsets.ViewSet):
    queryset = Post.objects.all().order_by('created_on')
    serializer_class = PostSerializer

    def list(self, request, username):
        user = User.objects.get(username=username)
        queryset = Post.objects.filter(author=user).order_by('created_on')
        serializer = PostSerializer(queryset, many=True)

        page = request.GET.get("page",1)
        size = request.GET.get("size",5)

        page, size = paginationGetter(page, size)

        postData = serializer.data[((page-1)*size):page*size]

        data = {}
        data["type"] = "posts"
        data["page"] = page
        data["size"] = (len(serializer.data) // 5) + 1
        data["items"] = postData

        return Response(data)

    def retrieve(self, request, username, post_ID):
        user = User.objects.get(username=username)
        queryset = Post.objects.get(ID=post_ID)
        serializer = PostSerializer(queryset)
        return Response(serializer.data)

class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
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
        data["size"] = (len(serializer.data) // 5) + 1
        data["items"] = userData
        return Response(data)

    def retrieve(self, request, pk=None):
        queryset = UserProfile.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user.user)
        return Response(serializer.data)

class CommentViewSet(viewsets.ViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """
    queryset = Post.objects.all().order_by('created_on')
    serializer_class = CommentSerializer

    def list(self, request, username, post_ID):
        user = User.objects.get(username=username)
        post = Post.objects.get(ID=post_ID)
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
        data["size"] = (len(serializer.data) // 5) + 1
        data["post"] = host + post.author.username + "/articles/" + str(post.ID) + "/comments"
        data["comments"] = commentData
        return Response(data)

    def retrieve(self, request, username, post_ID, comment_ID):
        user = User.objects.get(username=username)
        post = Post.objects.get(ID=post_ID)
        comments = Comment.objects.get(id=comment_ID)
        serializer = CommentSerializer(comments)
        return Response(serializer.data)

class LikeViewSet(viewsets.ViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """

    def commentList(self, request, username, post_ID, comment_ID):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }
        comment = Comment.objects.get(ID=comment_ID)
        likes = Like.objects.filter(comment=comment)
        serializer = LikeSerializer(likes, many=True, context=serializer_context)

        likeData = serializer.data
        data = {}
        data["type"] = "likes"
        data["items"] = likeData
        return Response(data)

    def postList(self, request, username, post_ID):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }
        post = Post.objects.get(ID=post_ID)
        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True, context=serializer_context)

        likeData = serializer.data
        data = {}
        data["type"] = "likes"
        data["items"] = likeData
        return Response(data)

    def authorList(self, request, username):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }

        author = User.objects.get(username=username)
        likes = Like.objects.filter(author=author)
        serializer = LikeSerializer(likes, many=True, context=serializer_context)

        likeData = serializer.data
        for like in likeData:
            del like["author"]
        data = {}
        data["type"] = "liked"
        data["items"] = likeData
        return Response(data)

class StreamView(generic.ListView):
    model = Post
    template_name = "unhindled/mystream.html"
    ordering = ['-created_on']

    def get(self, request, *args, **kwargs):
        response = requests.get(f'https://api.github.com/users/{request.user}/events/public', auth=GITHUB_AUTH)
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
    model = Friendship
    template_name = "unhindled/friends.html"
    fields = "__all__"
    

def friendRequest(request):
    if User.objects.filter(username=request.POST["adressee"]).count() == 1 and Friendship.objects.filter(adresseeId=request.POST["adressee"],requesterId=request.user.username).count() == 0 and Friendship.objects.filter(adresseeId=request.user.username,requesterId=request.POST["adressee"]).count() == 0: 
    	x = Friendship.objects.create(requesterId=request.user.username, adresseeId=request.POST["adressee"], status="pending")
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)
    

def friendRequestAccept(request):
   friendship = Friendship.objects.get(requesterId=request.POST["follower"],adresseeId=request.user.username)
   friendship.status="accepted"
   friendship.save()
   next = request.POST.get('next', '/')
   return HttpResponseRedirect(next)


def unfriend(request):
   friendship = Friendship.objects.get(requesterId=request.POST["requester"],adresseeId=request.POST["adressee"])
   friendship.delete()
   next = request.POST.get('next', '/')
   return HttpResponseRedirect(next)


class CreatePostView(generic.CreateView):
    model = Post
    template_name = "unhindled/create_post.html"
    fields = "__all__"


# def SharePost(request, user, post_id):
#     return HttpResponseRedirect(reverse('index'))


class SharePost(generic.View):
    def get(self, request, user, pk):
        post_object = get_object_or_404(Post, pk=pk)
        current_user = request.user
        if current_user == AnonymousUser:
            return HttpResponseRedirect(reverse('viewPost', args=(str(current_user ), post_object.ID)))

        if post_object.is_shared_post:
            post_object = post_object.originalPost

        sharedPost = Post.objects.create(author=post_object.author, contentType=post_object.contentType,
        title=post_object.title, description=post_object.description,
        visibility=post_object.visibility, created_on=post_object.created_on, content=post_object.content,
        images=post_object.images, originalPost=post_object, sharedBy=current_user).save()
        return HttpResponseRedirect(reverse('index'))
  
def likeObject(request, user, id, obj_type):
    author = User.objects.get(username=user)
    if obj_type == "comment":
        comment = Comment.objects.get(ID = id)
        existingLike = Like.objects.filter(comment=comment,author=author)
        if (len(existingLike) == 0):
            like = Like(comment=comment,author=author)
            like.save()
        post = comment.post
    elif obj_type == "post":
        post = Post.objects.get(ID = id)
        existingLike = Like.objects.filter(post=post,author=author)
        if (len(existingLike) == 0):
            like = Like(post=post,author=author)
            like.save()

    return HttpResponseRedirect(post.get_absolute_url())

def unlikeObject(request, user, id, obj_type):
    author = User.objects.get(username=user)
    if obj_type == "comment":
        comment = Comment.objects.get(ID = id)
        existingLike = Like.objects.filter(comment=comment,author=author)
        if (len(existingLike) >= 1):
            existingLike.delete()
        post = comment.post
    elif obj_type == "post":
        post = Post.objects.get(ID = id)
        existingLike = Like.objects.filter(post=post,author=author)
        if (len(existingLike) >= 1):
            existingLike.delete()

    return HttpResponseRedirect(post.get_absolute_url())


def view_post(request, user, pk):
    post = get_object_or_404(Post, ID=pk)
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
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        user_post = Post.objects.filter(author=user).order_by('-created_on')

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
