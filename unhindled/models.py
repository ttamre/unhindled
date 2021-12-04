import uuid
from django.db import models
from django.db.models.fields import EmailField
from django.urls import reverse
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	username = models.CharField(max_length=100, unique=True)
	displayName = models.CharField(max_length=100, null=True)
	password = models.CharField(max_length=100)

	def save(self, *args, **kwargs):
		self.displayName = self.username
		super(User, self).save(*args, **kwargs)
	
#maybe not best implementation
class Follower(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.CharField(max_length=200)
	follower = models.CharField(max_length=200)
	class Meta:
        	unique_together = (("author", "follower"),)
        	
class FollowRequest(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.CharField(max_length=200)
	follower = models.CharField(max_length=200)
	class Meta:
        	unique_together = (("author", "follower"),)	


class Post(models.Model):
	CONTENT_TYPES = (
		('text/markdown', 'Markdown'),
		('text/plain','Plaintext'),
	)
	VISIBILITY = (
		('PUBLIC', 'Public'),
		('FRIENDS', 'Friends Only'),
		('SEND', 'Send to Author')
	)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	contentType = models.CharField(max_length=20, choices=CONTENT_TYPES, default=CONTENT_TYPES[1][0],null=False)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	visibility = models.CharField(max_length=14, choices=VISIBILITY, default=VISIBILITY[0][0], null=False)
	send_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_to', null=True, blank=True)
	published = models.DateTimeField(auto_now_add=True)
	source = models.CharField(max_length=50, default="https://unhindled.herokuapp.com/")
	#will need to change
	content = models.TextField(blank=True)
	images = models.ImageField(null=True,blank=True, upload_to='images/')
	unlisted = models.BooleanField(default=False)
	#class Meta:
		#abstract = True

	sharedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_by', null=True, blank=True, editable =False)
	originalPost = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True, editable =False)

	def create_post(sender, instance, created, **kwargs):
		if created:
			post = Post(user=instance, author=instance.displayName)
			post.save()

	@property
	def is_shared_post(self):
		return self.sharedBy != None

	def get_absolute_url(self):
		return reverse('viewPost', args=(str(self.author), self.pk))

	def clean(self):
		if not (self.images or self.content):
			raise ValidationError('Invalid Value')

class Comment(models.Model):
	CONTENT_TYPES = (
		('md', 'text/markdown'),
		('txt','text/plain'),
	)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment')
	comment = models.TextField(blank=True, max_length=500)
	contentType = models.CharField(max_length=4, choices=CONTENT_TYPES, default=CONTENT_TYPES[0][0],null=False)
	published = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.comment

class Like(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

class UserProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
	displayName = models.CharField(max_length=20, blank=True, null=True)
	email = models.EmailField(max_length=254, blank=True, null=True)
	date_of_birth = models.DateField(null=True, blank=True)
	location = models.CharField(max_length=100, default="", blank=True, null=True)
	more_info = models.TextField(max_length=500, default="", blank=True)
	github = models.CharField(max_length=100, default="", blank=True, null=True)
	profileImage = models.ImageField(upload_to='upload/profile_photos/', default='upload/profile_photos/default.png', blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		userProfile = UserProfile(user=instance, displayName=instance.username)
		userProfile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()
