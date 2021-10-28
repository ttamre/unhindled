from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Post, Author, Friendship, UserProfile
from .forms import FriendRequestForm

# Create your views here.

class HomeView(generic.ListView):
    model = Post
    template_name = "unhindled/index.html"
    ordering = ['-created_on']

class StreamView(generic.ListView):
    model = Post
    template_name = "unhindled/mystream.html"
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
    if User.objects.filter(username=request.POST["adressee"]).count() == 1 and Friendship.objects.filter(adresseeId=request.POST["adressee"],requesterId=request.user.username).count() == 0:
    	x = Friendship.objects.create(requesterId=request.user.username, adresseeId=request.POST["adressee"], status="pn")
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

class CreatePostView(generic.CreateView):
    model = Post
    template_name = "unhindled/create_post.html"
    fields = "__all__"

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

# def SharePost(request, user, post_id):
#     return HttpResponseRedirect(reverse('index'))
  
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
