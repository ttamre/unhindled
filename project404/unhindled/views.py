from django.contrib.auth import login
from django.shortcuts import render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Post, Author, UserProfile

import requests
import json
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
        # events = requests.get(f'https://api.github.com/users/ttamre/events/public').json()
        event_list = [
            {"repo": "1", "url": 'link to repo 1', "issue": 'issue'},
            {"repo": "2", "url": 'link to repo 2', "issue": 'issue'},
            {"repo": "3", "url": 'link to repo 3', "issue": 'issue'}
        ]
        # for event in events:
            # repo = event.get("repo", {}).get("name")
            # url  = event.get("repo", {}).get("url")
            # issue = event.get("payload", {}).get("issue", {}).get("number")

            # context.append({"repo": repo, "url": url, "issue": issue})

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