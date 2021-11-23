import uuid
from django.db import models
from django.urls import reverse
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

#maybe not best implementation
class Friendship(models.Model):
	FRIEND_STATUS = (
		('pending', 'Pending'),
		('accepted', 'Accepted'),
	)
	ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	requesterId = models.CharField(max_length=100)
	adresseeId = models.CharField(max_length=100)
	status = models.CharField(max_length=10, choices=FRIEND_STATUS, default=FRIEND_STATUS[0][0])
	class Meta:
			unique_together = (('requesterId', 'adresseeId'),)

class Post(models.Model):
	CONTENT_TYPES = (
		('md', 'text/markdown'),
		('txt','text/plain'),
	)
	VISIBILITY = (
		('public', 'Public'),
		('unlisted', 'Unlisted'),
		('friends', 'Friends Only'),
		('send', 'Send to Author')
	)
	ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	contentType = models.CharField(max_length=4, choices=CONTENT_TYPES, default=CONTENT_TYPES[1][0],null=False)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	visibility = models.CharField(max_length=14, choices=VISIBILITY, default=VISIBILITY[0][0], null=False)
	send_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_to', null=True, blank=True)
	created_on = models.DateTimeField(auto_now_add=True)
	#will need to change
	content = models.TextField(blank=True)
	images = models.ImageField(null=True,blank=True, upload_to='images/')
	#class Meta:
		#abstract = True

	sharedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_by', null=True, blank=True, editable =False)
	originalPost = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True, editable =False)

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
	ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment')
	comment = models.TextField(blank=True, max_length=500)
	contentType = models.CharField(max_length=4, choices=CONTENT_TYPES, default=CONTENT_TYPES[0][0],null=False)
	published = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.comment

class Like(models.Model):
	ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

class UserProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
	displayName = models.CharField(max_length=20, blank=True, null=True)
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