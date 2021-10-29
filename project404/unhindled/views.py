from django.contrib.auth import login
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Post, Author, UserProfile, Comment
from .forms import *
# Create your views here.

class HomeView(generic.ListView):
    model = Post
    template_name = "unhindled/index.html"
    ordering = ['-created_on']
    
class AccountView(generic.CreateView):
    model = Author
    template_name = "unhindled/account.html"
    fields = "__all__"

class CreatePostView(generic.CreateView):
    model = Post
    template_name = "unhindled/create_post.html"
    fields = "__all__"


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

# class PostView(generic.DetailView):
#     model = Post
#     template_name = "unhindled/view_post.html"

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
