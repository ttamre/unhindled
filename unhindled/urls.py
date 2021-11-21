from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('post/', views.CreatePostView.as_view(), name='createPost'),
    path('mystream/', views.StreamView.as_view(), name='mystream'),
    path('account', views.AccountView.as_view(), name='account'),
    path('<str:user>/friends', views.ManageFriendView.as_view(), name='friends'),
    path('friend_request', views.friendRequest),
    path('friend_request_accept', views.friendRequestAccept),
    path('unfriend', views.unfriend),
    path('profile/<str:pk>/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/<str:pk>/', views.EditProfileView.as_view(), name='editProfile'),
    path('<str:user>/articles/<str:pk>', views.view_post, name='viewPost'),
    path('<str:user>/articles/<str:pk>/edit', views.UpdatePostView.as_view(), name='updatePost'),
    path('<str:user>/articles/<str:pk>/delete', views.DeletePostView.as_view(), name='deletePost'),
    path('<str:user>/articles/<str:pk>/share', views.SharePost.as_view(), name='sharePost'),
]
