from django.db.models.fields import Field
from rest_framework import serializers

from .models import Post
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'is_superuser')

class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    host = "httls://127.0.0.1:8000"
    class Meta:
        model = Post
        fields = ('ID', 'author', 'contentType', 'title', 'description','visibility', 'created_on')
        depth = 1

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['type'] = 'post'
        data['source'] = self.host + "/" + obj.author.username + "/articles/" + str(obj.ID)
        data['origin'] = self.host + "/" + obj.author.username + "/articles/" + str(obj.ID)
        return data

