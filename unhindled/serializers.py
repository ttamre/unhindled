from django.db.models import fields
from django.db.models.fields import Field
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Follower, FollowRequest, UserProfile, Comment, Like

User = get_user_model()

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):

    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = UserProfile
        fields = ('displayName','github','profileImage')

class UserSerializer(serializers.HyperlinkedModelSerializer):

    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = User
        fields = ('displayName','email', 'first_name', 'last_name')

    def to_representation(self, obj):
        data = super().to_representation(obj)
        userProfile = UserProfile.objects.get(user=obj)
        profileData = UserProfileSerializer(userProfile)
        data.update(profileData.data)
        if (data["profileImage"] is None) == False:
            data["profileImage"] = self.host[:-1] + str(data["profileImage"])
        data["url"] = self.host + "author/" + str(userProfile.pk)
        data["host"] = self.host + "author/" + str(userProfile.pk)
        data["id"] = self.host + "author/" + str(userProfile.pk)
        data["type"] = "author"
        return data
        

class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    host = "https://unhindled.herokuapp.com/"
    class Meta:
        model = Post
        fields = ('id', 'author','content', 'contentType', 'title', 'description','visibility', 'published')
        depth = 1

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["id"] = self.host + "author/" + str(obj.author.id) + "/posts/" + str(obj.id)
        data['type'] = 'post'
        data['source'] = self.host + "author/" + str(obj.author.id) + "/posts/" + str(obj.id)
        data['origin'] = self.host + "author/" + str(obj.author.id) + "/posts/" + str(obj.id)
        return data

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Comment
        fields = ('author','comment','contentType','published','id')
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
        fields = ( 'id', 'follower' )
        depth = 1
    def to_representation(self, obj):
    	data = super().to_representation(obj)
    	data["id"] = self.host + "author/" + obj.follower.displayName
    	data["url"] = self.host + "author/" + obj.follower.displayName
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
        data = super().to_representation(obj)
        data["object"] = obj.author
        data["actor"] = obj.follower
        data["type"] = "follow"
        return data

class LikeSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()
    comment = CommentSerializer()
    host = "https://unhindled.herokuapp.com/"
    post = PostSerializer()
    class Meta:
        model = Like
        fields = ('author', 'comment', 'post', 'id')
        depth = 1

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["type"] = "Like"
        if data["post"] is not None:
            data["object"] = self.host + obj.author.id + "/posts/" + str(obj.post.id)
            data["summary"] = str(obj.author.displayName) + " likes your post"
            data["post"] = self.host + obj.author.id + "/posts/" + str(obj.post.id)
        elif data["comment"] is not None:
            data["object"] = self.host + obj.author.id + "/posts/" + str(obj.comment.post.id) + "/comments/" + str(obj.comment.id)
            data["summary"] = str(obj.author.id) + " likes your comment"
            data["comment"] = str(obj.comment.id)
            data["post"] = self.host + obj.author.id + "/posts/" + str(obj.comment.post.id)
        
        return data

