from django.contrib.auth import login
from django.shortcuts import render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from requests.models import HTTPBasicAuth
from .models import Post, Author, UserProfile

import requests

GITHUB_EVENTS = {
    "CreateEvent": "Created repository",
    "PushEvent":   "Pushed code",
    "PullEvent":   "Pulled code",
    "ForkEvent":   "Forked repo",
    "MemberEvent": "Managed contributors",
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
        # TODO: User's own github profile, OAuth

        # Unauthorized API requests: 60 per hour
        events = requests.get(f'https://api.github.com/users/ttamre/events/public', auth=HTTPBasicAuth('user','pass')).json()
        event_list = []

        # Temporary - placeholder data for if we run out of api requests
        if "message" in events:
            event_list = [
                {"repo": "Repo 1", "url": 'link to repo 1', "issue": '9'},
                {"repo": "Repo 2", "url": 'link to repo 2', "issue": '62'},
                {"repo": "Repo 3", "url": 'link to repo 3', "issue": '35'}
            ]

        for event in events:
            repo = event.get("repo", {}).get("name")
            url  = event.get("repo", {}).get("url")
            type_ = GITHUB_EVENTS.get(event.get("type"))

            event_list.append({"repo": repo, "url": url, "type": type_})

        return render(request, 'unhindled/mystream.html', {"context": event_list})

class AccountView(generic.CreateView):
    model = Author
    template_name = "unhindled/account.html"
    fields = "__all__"

class CreatePostView(generic.CreateView):
    model = Post
    template_name = "unhindled/create_post.html"
    fields = "__all__"

class PostView(generic.DetailView):
    model = Post
    template_name = "unhindled/view_post.html"

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
    fields = ['name', 'date_of_birth',  'location', 'more_info', 'photo']
    template_name = 'unhindled/edit_profile.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user