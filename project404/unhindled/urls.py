from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('post/', views.CreatePostView.as_view(), name='createPost'),
    path('inprogress/', views.HomeView.as_view(), name='stream'),
    path('account', views.AccountView.as_view(), name='account'),
    path('<str:user>/articles/<str:pk>', views.PostView.as_view(), name='viewPost'),
    path('<str:user>/articles/<str:pk>/edit', views.UpdatePostView.as_view(), name='updatePost'),
    path('<str:user>/articles/<str:pk>/delete', views.DeletePostView.as_view(), name='deletePost'),
    path('profile/<str:pk>/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/<str:pk>/', views.EditProfileView.as_view(), name='editProfile'),

]
