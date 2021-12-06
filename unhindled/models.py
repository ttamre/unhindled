import uuid
from django.db import models
from django.db.models.fields import EmailField
from django.db.models.fields.related import ForeignKey
from django.urls import reverse
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, post_save
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

class ForeignAuthor(models.Model):
	id = models.CharField(primary_key=True, max_length=200, unique=True)
	host = models.CharField(max_length=200)
	displayName = models.CharField(max_length=100)
	github = models.CharField(max_length=200, null=True, blank=True, default="")
	profileImage = models.CharField(max_length=200, null=True, blank=True, default="")

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
	author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
	contentType = models.CharField(max_length=20, choices=CONTENT_TYPES, default=CONTENT_TYPES[1][0],null=False)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	visibility = models.CharField(max_length=14, choices=VISIBILITY, default=VISIBILITY[0][0], null=False)
	send_to = models.CharField(max_length=300, null=True, blank=True, default=None)
	published = models.DateTimeField(auto_now_add=True)
	source = models.CharField(max_length=50, default="https://unhindled.herokuapp.com/", editable=False)
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
			raise ValidationError('ERROR: post missing content or image')
		if self.visibility == "SEND" and self.send_to is None:
			raise ValidationError("ERROR: Need to specify author when Send to Author is Selected")

class Comment(models.Model):
	CONTENT_TYPES = (
		('md', 'text/markdown'),
		('txt','text/plain'),
	)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,default=None)
	foreign_author = models.ForeignKey(ForeignAuthor, on_delete=models.CASCADE,blank=True,null=True,default=None)
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
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	foreign_author = models.ForeignKey(ForeignAuthor, on_delete=models.CASCADE,blank=True,null=True,default=None)

class UserProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
	displayName = models.CharField(max_length=20, blank=True, null=True)
	email = models.EmailField(max_length=254, blank=True, null=True)
	date_of_birth = models.DateField(null=True, blank=True)
	location = models.CharField(max_length=100, default="", blank=True, null=True)
	more_info = models.TextField(max_length=500, default="", blank=True)
	github = models.CharField(max_length=100, default="", blank=True, null=True)
	profileImage = models.ImageField(upload_to='upload/profile_photos/', default='upload/profile_photos/default.png')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		userProfile = UserProfile(user=instance, displayName=instance.username)
		userProfile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

class Inbox(models.Model):
	ITEM_TYPES = (
		('post', 'post'),
		('like', 'like'),
		('follow', 'follow'),
		('comment', 'comment')
	)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	inbox_of = models.ForeignKey(User, related_name="inbox_of", on_delete=models.CASCADE)
	inbox_from = models.CharField(max_length=200)
	type = models.CharField(max_length=7, choices=ITEM_TYPES, default=ITEM_TYPES[0][0])
	link = models.URLField()
	seen = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
	like = models.ForeignKey(Like, on_delete=models.CASCADE, blank=True, null=True)
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)


@receiver(post_save, sender=Post)
def send_post_to_local_inbox(sender, instance, created, **kwargs):
	from unhindled.connect import send_post_to_inbox
	if created:
		if (instance.send_to is not None) and instance.visibility == "SEND":
			if str(instance.send_to).startswith("http"):
				send_post_to_inbox(instance.send_to, instance)
			else:
				link = "https://unhindled.herokuapp.com/"
				link += "author/" + str(instance.author.id) + "/posts/" + str(instance.id)
				id = uuid.UUID(instance.send_to)
				receiver = User.objects.get(id=id)
				inbox = Inbox(inbox_of=receiver, type="post",link=link, inbox_from=instance.author.username,post=instance)
				inbox.save()
		
		else:
			followers = Follower.objects.filter(author=instance.author)
			for follower in followers:
				link = "https://unhindled.herokuapp.com/"
				link += "author/" + str(instance.author.username) + "/posts/" + str(instance.id)
				inbox = Inbox(inbox_of=follower.follower, type="post",link=link, inbox_from=instance.author.username,post=instance)
				inbox.save()

@receiver(post_save, sender=Like)
def send_like_to_local_inbox(sender, instance, created, **kwargs):
	if created:
		if instance.post is not None:
			if instance.post.author != instance.author:
				link = "https://unhindled.herokuapp.com/"
				link += "author/" + str(instance.post.author.username) + "/posts/" + str(instance.post.id)
				inbox = Inbox(inbox_of=instance.post.author, type="like",link=link, inbox_from=instance.author,like=instance)
				inbox.save()

@receiver(post_save, sender=Comment)
def send_comment_to_local_inbox(sender, instance, created, **kwargs):
	if created:
		if instance.post is not None:
			if instance.post.author != instance.author:
				link = "https://unhindled.herokuapp.com/"
				link += "author/" + str(instance.post.author.username) + "/posts/" + str(instance.post.id)
				inbox = Inbox(inbox_of=instance.post.author, type="comment",link=link, inbox_from=instance.author,comment=instance)
				inbox.save()