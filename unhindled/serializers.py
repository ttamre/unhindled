from django.db.models.fields import Field
from rest_framework import serializers

from django.contrib.auth.models import User
from .models import Post, Author, Follower, FollowRequest, UserProfile, Comment

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):

    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = UserProfile
        fields = ('displayName','github','profileImage')

class UserSerializer(serializers.HyperlinkedModelSerializer):

    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = User
        fields = ('username','email', 'first_name', 'last_name')

    def to_representation(self, obj):
        data = super().to_representation(obj)
        userProfile = UserProfile.objects.get(user=obj)
        profileData = UserProfileSerializer(userProfile)
        data.update(profileData.data)
        data["profileImage"] = self.host[:-1] + data["profileImage"]
        data["url"] = self.host + "profile/" + str(userProfile.pk)
        data["host"] = self.host + "profile/" + str(userProfile.pk)
        data["id"] = self.host + "profile/" + str(userProfile.pk)
        data["type"] = "author"
        return data
        

class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = Post
        fields = ('ID', 'author', 'contentType', 'title', 'description','visibility', 'created_on')
        depth = 1

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['type'] = 'post'
        data['source'] = self.host + obj.author.username + "/articles/" + str(obj.ID)
        data['origin'] = self.host + obj.author.username + "/articles/" + str(obj.ID)
        return data

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Comment
        fields = ('author','comment','contentType','published','ID')
        depth = 1
        
    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["type"] = "comment"
        return data

#for URL: ://service/author/{AUTHOR_ID}/followers
#TODO add github to UserProfile
#TODO figure out host
#maybe can be combined by AuthorSerializer
class FollowerListSerializer(ModelSerializer):
    id = "http://127.0.0.1:5454/" + "author/" + author
    url = "http://127.0.0.1:5454/" + "author/" + author
    host = "http://127.0.0.1:5454/"
    type = "author"
    class Meta:
        model = UserProfile
        fields = ( 'displayName', 'profileImage', 'github', )
#for URL: ://service/author/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}                  
class FollowerSerializer(ModelSerializer):
    class Meta:
        model = Follower


class FollowRequestSerializer(ModelSerializer):
    type = "Follow"
    summary = UserProfile.objects.get(author).displayName + " wants " + UserProfile.objects.get(follower).displayName + " to follow them."
    actor = UserProfile.objects.get(follower)
    object = UserProfile.objects.get(author)
    class Meta:
        model = FollowRequest
