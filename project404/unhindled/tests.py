from django.test import TestCase, Client
from django.urls import reverse
from unhindled.models import *
from django.contrib.auth.models import User
from .models import Post, Friendship, Comment
import datetime

# User tests
class UserTests(TestCase):
  def setup(self):
    self.user = User.objects.create_user(username="user1", email="u@u.com")
    self.user.set_password('password1')
    self.user.save()

  # Make test when user creation is added
  # def create_user(self):
  #   data = {'username': "user1", 'email': "u@u.com", 'password': "password1"}

  def test_login(self):
    c = Client()
    c.login(username='user1', password='password1')
    c.get('/')

class HTMLTests(TestCase):
  def setup(self):
    self.user = User.objects.create_user(username="user1", email="u@u.com")
    self.user.set_password('password1')
    self.user.save()

  def test_index(self):
    resp = self.client.get(reverse("index"))
    self.assertEqual(resp.status_code, 200)
    self.assertContains(resp, '<p>No Posts to show.</p>')

  def test_login_index(self):
    resp = self.client.get(reverse("index"))
    self.assertContains(resp, '<p>No Posts to show.</p>')

    resp = self.client.post(reverse("login"), {'username': 'user1', 'password': 'password1'})
    print(resp.content)
    # self.assertTrue(resp.context['user'].is_authenticated)
    # self.assertRedirects(resp, reverse("index"), 302)

    # print(resp.content)

    # resp = c.get(reverse("index"))
    # # print(resp.content)
    # self.assertContains(resp, '<p class="non-white-title">HOME</p>')
    
class FriendshipTests(TestCase):
   def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='12345')
        self.user1.save()
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.user2.save()
        login = self.client.login(username='testuser', password='12345')
        
   def test_friendships(self):
   	friendship = Friendship.objects.create(requesterId='testuser',adresseeId='testuser2')
   	friendship.save()
   	self.assertEqual(len(Friendship.objects.filter(requesterId = self.user1.username).values_list('ID', flat=True)),1)
   	friendship = Friendship.objects.filter(requesterId = self.user1.username)[0]
   	self.assertEqual(friendship.status, "pending")
   	
class CommentTests(TestCase):
   def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user.save()
        login = self.client.login(username='testuser', password='12345')
        self.new_post = Post.objects.create(author=self.user, 
		title="Test Title", description="This is a test Post",
		visibility=Post.VISIBILITY[0], created_on=datetime.datetime.now(), content="TEST POST 1",
		images=None, originalPost=None, sharedBy=None)
        self.new_post.save()
        
   def test_comments(self):
   	comment = Comment.objects.create(author=self.user,post=self.new_post,comment='test comment' )
   	comment.save()
   	self.assertEqual(len(Comment.objects.filter(author=self.user).values_list('ID', flat=True)),1)
   	
class UserProfileTests(TestCase):
   def setUp(self):
        self.user = User.objects.create_user(id=12345678,username='testuser', password='12345')
        self.user.save()
        login = self.client.login(username='testuser', password='12345')
        
   def test_user_profile(self):
   	user_profile = UserProfile.objects.filter(user_id = self.user.id)[0]
   	user_profile.date_of_birth=datetime.date(2000,1,1) 
   	user_profile.save()
   	self.assertEqual(UserProfile.objects.filter(user_id=self.user.id).values_list('date_of_birth', flat=True)[0],datetime.date(2000,1,1))
   	
