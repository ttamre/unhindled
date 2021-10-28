from django.contrib.auth import login
from django.shortcuts import render
from django.urls.base import reverse
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .models import Post, Author, Friendship
from .forms import FriendRequestForm
# Create your views here.

class HomeView(generic.ListView):
    model = Post
    template_name = "unhindled/index.html"
    ordering = ['-created_on']
    
class AccountView(generic.CreateView):
    model = Author
    template_name = "unhindled/account.html"
    fields = "__all__"

class ManageFriendView(generic.ListView):
    model = Friendship
    template_name = "unhindled/friends.html"
    fields = "__all__"
    
def friendRequest(request):
    if Author.objects.filter(ID=request.POST["adressee"]).count() == 1 and Friendship.objects.filter(adresseeId=request.POST["adressee"],requesterId=request.user.username).count() == 0:
    	x = Friendship.objects.create(requesterId=request.user.username, adresseeId=request.POST["adressee"], status="pn")
    return render(request, 'unhindled/friends.html')

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

