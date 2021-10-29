from django.test import TestCase
from .models import Post
from django.contrib.auth.models import User
import datetime

# Create your tests here.

class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user.save()
        login = self.client.login(username='testuser', password='12345')
        self.posts_to_delete = []
        # self.new_post = Post.objects.create(author=self.user, contentType=Post.CONTENT_TYPES[0], 
        # title="Test Title", description="This is a test Post",
        # visibility=Post.VISIBILITY[0] created_on=datetime.datetime.now(), content="TEST POST",
        # images=None, originalPost=None, sharedBy=None)

    def tearDown(self):
        User.objects.filter(username = self.user).delete()
        for post in self.posts_to_delete:
            Post.objects.filter(ID=post).delete()

    def test_addingPosts(self):
        existing_ID_query = Post.objects.filter(title="Test Title").values_list('ID', flat=True)
        totalID = len(existing_ID_query)
        response = self.client.post("/post/",data={"author":self.user.pk, "contentType":"md", 
        "title":"Test Title", "description":"This is a test Post",
        "visibility":"public", "created_on":datetime.datetime.now(), "content":"TEST POST",
        "images":"", "originalPost":"", "sharedBy":""})
        id_to_delete = ""
        
        addedPost = Post.objects.filter(title="Test Title").values_list('ID', flat=True)
        self.assertEqual(len(addedPost), totalID + 1)
        for id_val in list(addedPost):
            if id_val not in list(existing_ID_query):
                id_to_delete = addedPost[0]
                self.posts_to_delete.append(id_to_delete)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/" + self.user.username + "/articles/" + str(id_to_delete))

        

