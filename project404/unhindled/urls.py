from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('post/', views.CreatePostView.as_view(), name='createPost'),
    path('<str:user>/', views.HomeView.as_view(), name='stream'),
    path('inprogress/', views.HomeView.as_view(), name='viewPost'),
]