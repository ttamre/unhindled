from django.test import TestCase
from .models import Post
from django.contrib.auth.models import User
import datetime

# Create your tests here.

class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='testuser2', password='12345')
        self.user.save()
        self.other_user.save()
        login = self.client.login(username='testuser', password='12345')
        self.posts_to_delete = []
        self.new_post = Post.objects.create(author=self.user, contentType=Post.CONTENT_TYPES[0], 
        title="Test Title", description="This is a test Post",
        visibility=Post.VISIBILITY[0], created_on=datetime.datetime.now(), content="TEST POST 1",
        images=None, originalPost=None, sharedBy=None)
        self.new_post.save()

    def tearDown(self):
        User.objects.filter(username = self.user).delete()
        self.new_post.delete()
        for post in self.posts_to_delete:
            Post.objects.filter(ID=post).delete()

    def test_addingPosts(self):
        # Adding post and checking if post is added
        existing_ID_query = Post.objects.filter(title="Test Title").values_list('ID', flat=True)
        
        totalID = len(existing_ID_query)
        response = self.client.post("/post/",data={"author":self.user.pk, "contentType":"md", 
        "title":"Test Title", "description":"This is a test Post",
        "visibility":"public", "created_on":datetime.datetime.now(), "content":"TEST POST 2",
        "images":"", "originalPost":"", "sharedBy":""})
        id_to_delete = ""
        
        addedPost = Post.objects.filter(title="Test Title").values_list('ID', flat=True)
        self.assertEqual(len(addedPost), totalID + 1)
        for id_val in list(addedPost):
            if id_val not in list(existing_ID_query):
                id_to_delete = id_val
                self.posts_to_delete.append(id_to_delete)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/" + self.user.username + "/articles/" + str(id_to_delete))

    def test_edittingPosts(self):
        # Editing post and checking if post is edited
        response = self.client.post("/"+self.user.username + "/articles/" + str(self.new_post.ID) + "/edit",data={'author': ['1'], "contentType":["md"], 
        "title":["Test Title"], "description":["This is a test Post"],
        "visibility":["public"], "content":["TEST POST(EDITED)"],
        "images":[""], "originalPost":[""], "sharedBy":[""]})

        editedPost = Post.objects.filter(ID=self.new_post.ID)
        self.assertEqual(editedPost[0].content, "TEST POST(EDITED)")

    def test_deletingPosts(self):
        # Deleting post and checking if post is deleted
        oldPost = Post.objects.filter(ID=self.new_post.ID)
        self.assertEqual(len(oldPost), 1)
        response = self.client.post("/"+self.user.username + "/articles/" + str(self.new_post.ID) + "/delete")

        oldPost = Post.objects.filter(ID=self.new_post.ID)
        self.assertEqual(len(oldPost), 0)

    def test_sharingPosts(self):
        # Sharing post and checking if post is shared
        totalShare = Post.objects.filter(originalPost=self.new_post)
        totalShares = len(totalShare)
        response = self.client.get("/"+self.user.username + "/articles/" + str(self.new_post.ID) + "/share")

        totalShare = Post.objects.filter(originalPost=self.new_post)
        self.assertEqual(len(totalShare), totalShares + 1)

    def test_restrictions(self):
        other_post = Post.objects.create(author=self.other_user, contentType=Post.CONTENT_TYPES[0], 
        title="Test Title", description="This is a test Post",
        visibility=Post.VISIBILITY[0], created_on=datetime.datetime.now(), content="TEST POST 1",
        images=None, originalPost=None, sharedBy=None)
        other_post.save()

        response = self.client.get("/"+self.other_user.username + "/articles/" + str(other_post.ID))

        # Checking For unauthorized access
        # response_str = str(response.rendered_content)
        response_str = str(response.content)
        self.assertEqual("Edit" in response_str, False)
        self.assertEqual("Delete" in response_str, False)

        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get("/"+self.other_user.username + "/articles/" + str(other_post.ID))

        # Checking for authorized access
        response_str = str(response.content)
        self.assertEqual("Edit" in response_str, True)
        self.assertEqual("Delete" in response_str, True)







        


