from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser, User
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, Author, Follower, FollowRequest, UserProfile, Comment
from .forms import *
from .serializers import *
import requests
import json
import os

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


# Create your views here.
class HomeView(generic.ListView):
    model = Post
    template_name = "unhindled/index.html"
    ordering = ['-created_on']

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
    model = Author
    template_name = "unhindled/account.html"
    fields = "__all__"


class ManageFriendView(generic.ListView):
    model = Follower
    template_name = "unhindled/friends.html"
    fields = "__all__"
    
def follow(request):
    if User.objects.filter(username=request.POST["author"]).count() == 1 and \
       Follower.objects.filter(author=request.POST["author"],follower=request.user.username).count() == 0 :
        Follower.objects.create(follower=request.user.username, author=request.POST["author"])
        if Follower.objects.filter(author=request.user.username,follower=request.POST["author"]).count() == 0:
            FriendRequest.objects.create(author=request.user.username, follower=request.POST["author"])
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

def deleteFollowRequest(request):
    followRequest = FollowRequest.objects.get(author=request.POST["author"],follower=request.user.username)
    follow.delete()
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)    

def unfollow(request):
    follow = Follower.objects.get(author=request.POST["author"],follower=request.user.username)
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
    fields = ['displayName', 'date_of_birth',  'location', 'more_info', 'profileImage']
    template_name = 'unhindled/edit_profile.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user



#endpoint views 
class AuthorViewset (CreateModelMixin, RetrieveModelMixin):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    
class FollowerListViewset (ListModelMixin):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    
class FollowerViewset (RetrieveModelMixin,UpdateModelMixin, DestroyModelMixin):
    serializer_class = FollowerSerializer
    queryset = Follower.objects.all()
    
