from django.contrib.auth import login
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Like, Post, Follower, FollowRequest, UserProfile, Comment
from requests.models import Response as MyResponse
from rest_framework.response import Response
from .forms import *
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import *

import requests
import json
import os
import datetime, math

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
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
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
        data["size"] = math.ceil(len(serializer.data) / size)
        data["items"] = postData

        return Response(data)

    def retrieve(self, request, username, post_ID):
        user = User.objects.get(username=username)
        try:
            queryset = Post.objects.get(ID=post_ID)
        except:
            return Response({}, status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(queryset)
        return Response(serializer.data)

    def allPosts(self, request):
        posts = Post.objects.filter(visibility='public').order_by('created_on')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def createPost(self, request, username,post_ID=None):
        if post_ID != None:
            post = Post.objects.filter(ID=post_ID)
            if len(post) > 0:
                return Response({"Error":"Post ID already exists"}, status=status.HTTP_400_BAD_REQUEST)

        loggedInUser = request.user
        user = User.objects.get(username=username)

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

        visibility = 'public'
        for types in Post.VISIBILITY:
            if types[1].lower() == postData["visibility"].lower():
                visibility = types[0]

        send_to = None
        if ("sent_to" in postData.keys()):
            if (postData["sent_to"] is not None) and postData["sent_to"] != "":
                try:
                    send_to = User.objects.get(username=username)
                except:
                    send_to = User.objects.get(pk=postData["sent_to"])

        created_on = datetime.datetime.now()
        if ("published") in postData.keys():
            if (postData["published"] is not None) and postData["published"] != "":
                created_on = datetime.datetime(postData["published"])
        #will need to change
        content = postData.get("content",None)
        images = postData.get("images",None)

        try:
            newPost = Post(author=author,title=title,description=description,visibility=visibility,send_to=send_to,created_on=created_on,
                            content=content,contentType=contentType,images=images)
            if post_ID != None:
                newPost.ID = post_ID

            newPost.save()
            serializer = PostSerializer(newPost)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    def updatePost(self, request, username, post_ID):
        loggedInUser = request.user
        user = User.objects.get(username=username)
        try:
            postToEdit = Post.objects.get(ID=post_ID)
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
        if "created_on" in postData.keys() and postData["created_on"] != "":
            warning["created_on"] = "Published date can't be changed"
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

    def deletePost(self, request, username, post_ID):
        loggedInUser = request.user
        user = User.objects.get(username=username)
        try:
            postToDelete = Post.objects.get(ID=post_ID)
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
            user = User.objects.get(username=id)
        except:
            try:
                user = User.objects.get(pk=int(id))
            except:
                return Response({"Error": "User not found"}, status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def authorUpdate(self, request, id):
        try:
            user = User.objects.get(username=id)
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

        if "username" in updateData.keys() and updateData["username"] != "":
            otherUser = User.objects.filter(username=updateData["username"])
            if len(otherUser) > 0:
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            user.username = updateData["username"]
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
        data["size"] = math.ceil(len(serializer.data) / size)
        data["post"] = host + post.author.username + "/articles/" + str(post.ID) + "/comments"
        data["comments"] = commentData
        return Response(data)

    def retrieve(self, request, username, post_ID, comment_ID):
        user = User.objects.get(username=username)
        post = Post.objects.get(ID=post_ID)
        comments = Comment.objects.get(id=comment_ID)
        serializer = CommentSerializer(comments)
        return Response(serializer.data)

    def postComment(self, request, username, post_ID):
        loggedInUser = request.user
        try:
            post = Post.objects.get(ID=post_ID)
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
        authorObj = get_object_or_404(User, username=author)
        user = Follower.objects.filter(author=authorObj)
        serializer = FollowerListSerializer(user, many=True)
        return Response(serializer.data)
    
class FollowerViewset (viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, author, follower):
        authorObj = get_object_or_404(User, username=author)
        followerObj = get_object_or_404(User, username=follower)
        follow = get_object_or_404(Follower, author=authorObj, follower=followerObj)
        serializer = FollowerSerializer(follow)
        return Response(serializer.data)
    def update(self, request, author, follower):
        authorObj = get_object_or_404(User, username=author)
        followerObj = get_object_or_404(User, username=follower)
        Follower.objects.create(author=authorObj, follower=followerObj)
        follow = get_object_or_404(Follower, author=author, follower=follower)
        serializer = FollowerSerializer(follow)
        return Response(serializer.data)
    def destroy(self, request, author, follower):
        authorObj = get_object_or_404(User, username=author)
        followerObj = get_object_or_404(User, username=follower)
        follow = get_object_or_404(Follower, author=authorObj, follower=followerObj)
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

    def likePost(self, request, username, post_ID):
        loggedInUser = request.user
        try:
            post = Post.objects.get(ID=post_ID)
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

    def likeComment(self, request, username, post_ID, comment_ID):
        loggedInUser = request.user
        try:
            comment = Comment.objects.get(ID=comment_ID)
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
    model = Follower
    template_name = "unhindled/friends.html"
    fields = "__all__"
    
def follow(request):
    if User.objects.filter(username=request.POST["author"]).count() == 1:
       author = User.objects.get(username=request.POST["author"])
       if Follower.objects.filter(author=author,follower=request.user).count() == 0 :
           Follower.objects.create(follower=request.user, author=author)
           if Follower.objects.filter(author=request.user,follower=author).count() == 0 and FollowRequest.objects.filter(author=request.user,follower=author).count() == 0:
                FollowRequest.objects.create(author=request.user, follower=author)
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

def deleteFollowRequest(request):
    followRequest = FollowRequest.objects.get(author=request.POST["author"],follower=request.user.username)
    follow.delete()
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)    

def unfollow(request):
    author = User.objects.get(username=request.POST["author"])
    follow = Follower.objects.get(author=author,follower=request.user)
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


