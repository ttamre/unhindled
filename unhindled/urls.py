from django.urls import path, include
from . import views
urlpatterns = [
    #internal
    path('', views.HomeView.as_view(), name='index'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('post/', views.CreatePostView.as_view(), name='createPost'),
    path('<str:user_id>/mystream/', views.StreamView.as_view(), name='mystream'),
    path('account', views.AccountView.as_view(), name='account'),
    path('<str:user>/friends', views.ManageFriendView.as_view(), name='friends'),
    path('follow', views.follow),
    path('deleteFollowRequest', views.deleteFollowRequest),
    path('unfollow', views.unfollow),
    path('author/<str:id>', views.ProfileView.as_view(), name='profile'),
    path('author/<str:id>/edit', views.EditProfileView.as_view(), name='editProfile'),
    path('<str:user>/articles/<str:id>', views.view_post, name='viewPost'),
    path('<str:user>/articles/<str:id>/edit', views.UpdatePostView.as_view(), name='updatePost'),
    path('<str:user>/articles/<str:id>/delete', views.DeletePostView.as_view(), name='deletePost'),
    path('<str:user>/articles/<str:id>/share', views.SharePost.as_view(), name='sharePost'),
    path('<str:user>/like/<str:id>/<str:obj_type>', views.likeObject, name='likeObject'),
    path('<str:user>/unlike/<str:id>/<str:obj_type>', views.unlikeObject, name='unlikeObject'),
]
