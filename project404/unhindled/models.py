import uuid
from django.db import models
from django.urls import reverse
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Author(models.Model):
	ID = models.CharField(max_length=100, primary_key=True)
	displayName =  models.CharField(max_length=100)
	host = models.CharField(max_length=100)
	profileUrl = models.CharField(max_length=100)
	githubUrl = models.CharField(max_length=100)

	def __str__(self):
		return self.displayName

# leaving commented out because there is probably better implementations
#class Friend(models.Model):
	#author1 = models.ForeignKey(Author, on_delete=models.CASCADE)
	#author2 = models.ForeignKey(Author, on_delete=models.CASCADE)
	

class Post(models.Model):
	CONTENT_TYPES = (
		("md", "text/markdown"),
		("txt","text/plain"),
	)
	VISIBILITY = (
		("public", "Public"),
		("friends", "Friends Only"),
		("private", "Private"),
	)
	ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	contentType = models.CharField(max_length=4, choices=CONTENT_TYPES, default=CONTENT_TYPES[1],null=False)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	visibility = models.CharField(max_length=14, choices=VISIBILITY, default=VISIBILITY[0], null=False)
	created_on = models.DateTimeField(auto_now_add=True)
	#will need to change
	content = models.TextField(blank=True)
	images = models.ImageField(null=True,blank=True, upload_to='images/')
	#class Meta:
		#abstract = True

	def get_absolute_url(self):
		return reverse('viewPost', args=(str(self.author), self.pk))

	def clean(self):
		if not (self.images or self.content):
			raise ValidationError("You must specify either email or telephone")

#maybe use depending on implementation		
#class PublicPost(Post):
	#pass
#class FriendPost(Post):
	#pass
	
class Comment(models.Model):
	ID = models.CharField(max_length=100, primary_key=True)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	comment = models.CharField(max_length=1000)
	published = models.DateField()
	
	
