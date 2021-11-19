from rest_framework.serializers import ModelSerializer
from .models import Post, Author, Follower, FollowRequest, UserProfile, Comment

#for URL: ://service/author/{AUTHOR_ID}/  
class AuthorSerializer(ModelSerializer):
    id = "http://127.0.0.1:5454/" + "author/" + author
    url = "http://127.0.0.1:5454/" + "author/" + author
    host = "http://127.0.0.1:5454/"
    type = "author"
    class Meta:
        model = UserProfile
        fields = ( 'displayName', 'profileImage', 'github', )

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
#inprogress
class PostSerializer(ModelSerializer):
    type = "post"
    author = UserProfile.objects.get(user)
    url = serializers.CharField(source='get_absolute_url')
    id =
    count =
    published = created_on
    
    class Meta:
        model = Post
        fields = (
            'contentType', 'title', 'description', 'visibility',
            'content',
        )
class Comments(ModelSerializer):
    type = "comment"
    author = UserProfile.objects.get(author)
    id = "http://127.0.0.1:5454/" + "author/" + UserProfile.objects.get((Post.objects.get(post).author)).user \
        + "/posts/" + Post.objects.get(post).ID +"/comments/" + ID
    
    class Meta:
        model = Comment 
        fields = (
            'contentType', 'comment', 'published', 
        )        
