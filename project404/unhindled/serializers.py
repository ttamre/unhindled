from django.db.models.fields import Field
from rest_framework import serializers

from .models import Post, Friendship, User, UserProfile, Comment

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'is_superuser')

class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    host = "https://127.0.0.1:8000"
    class Meta:
        model = Post
        fields = ('id', 'author', 'contentType', 'title', 'description','visibility', 'created_on')
        depth = 1

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['type'] = 'post'
        data['source'] = self.host + "/" + obj.author.username + "/articles/" + str(obj.id)
        data['origin'] = self.host + "/" + obj.author.username + "/articles/" + str(obj.id)
        return data

