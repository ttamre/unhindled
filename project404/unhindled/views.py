from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse

from .models import Post
# Create your views here.

class HomeView(generic.ListView):
    model = Post
    template_name = "unhindled/index.html"

class CreatePostView(generic.CreateView):
    model = Post
    template_name = "unhindled/create_post.html"
    fields = "__all__"

class PostView(generic.DetailView):
    model = Post
    template_name = "unhindled/view_post.html"