from django.test import TestCase, Client
from django.urls import reverse
from unhindled.models import *
from django.contrib.auth.models import User

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
