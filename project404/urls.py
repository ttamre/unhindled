"""project404 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from unhindled import views

router = routers.DefaultRouter()
router.register(r'allposts', views.PostViewSet)
router.register(r'author', views.UserViewSet)

follower_actions = {
    "get": "retrieve",
    "delete": "destroy",
    "put": "update",
}

urlpatterns = [
    path('', include('unhindled.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('service/', include(router.urls)),
    path('service/allposts/', views.PostViewSet.as_view({'get':'allPosts'})),
    path('service/authors/', views.UserViewSet.as_view({'get':'list'}) ),
    path('service/author/<str:id>/', views.UserViewSet.as_view({'get': 'retrieve', 'post':'authorUpdate'}) ),
    path('service/author/<str:user_id>/liked', views.LikeViewSet.as_view({'get':'authorList'})),
    path('service/author/<str:user_id>/posts/', views.PostViewSet.as_view({'get':'list', 'post':'createPost'})),
    path('service/author/<str:user_id>/posts/<str:post_id>/', views.PostViewSet.as_view({'get':'retrieve', 'post':'updatePost', 'put':'createPost', 'delete':'deletePost'})),
    path('service/author/<str:user_id>/post/<str:post_id>/comments', views.CommentViewSet.as_view({'get':'list', 'post':'postComment'})),
    path('service/author/<str:user_id>/post/<str:post_id>/likes', views.LikeViewSet.as_view({'get':'postList', 'post':'likePost'})),
    path('service/author/<str:user_id>/post/<str:post_id>/comments/<str:comment_id>/likes', views.LikeViewSet.as_view({'get':'commentList', 'post':'likeComment'})),
    path('service/author/<str:author>/followers', views.FollowerListViewset.as_view({'get':'list'})), 
    path('service/author/<str:author>/followers/<str:follower>', views.FollowerViewset.as_view(actions=follower_actions)),
    path('service/author/<str:author>/friend_request/<str:follower>', views.FriendRequestViewset.as_view({'post':'create'})),
    path('service/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('foreign_posts', views.get_foreign_posts),
    path('foreign_authors', views.get_foreign_authors),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

