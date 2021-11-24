from django.db.models.fields import Field
from rest_framework import serializers

from django.contrib.auth.models import User
from .models import Post, Follower, FollowRequest, UserProfile, Comment

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
class FollowerListSerializer(serializers.HyperlinkedModelSerializer):
    follower = UserSerializer()
    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = Follower
        fields = ( 'ID', 'follower' )
        depth = 1
    def to_representation(self, obj):
    	data = super().to_representation(obj)
    	data["id"] = self.host + "author/" + obj.follower.username
    	data["url"] = self.host + "author/" + obj.follower.username
    	data["host"] = self.host 
    	data["type"] = "author" 
    	return data
#for URL: ://service/author/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}                  
class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'
#
#for URL: ://service/author/{AUTHOR_ID}/friend_request/{FOREIGN_AUTHOR_ID}
class FollowRequestSerializer(serializers.HyperlinkedModelSerializer):
    follower = UserSerializer()#UserProfile.objects.get(follower)
    author = UserSerializer()#UserProfile.objects.get(author)
    class Meta:
        model = FollowRequest
    def to_representation(self, obj):
    	data["object"] = obj.author
    	data["actor"] = obj.follower
    	data["type"] = "follow" 
    	return data

