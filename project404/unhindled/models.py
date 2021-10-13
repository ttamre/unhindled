from django.db import models

# Create your models here.

class Author(models.Model):
	ID = models.CharField(max_length=100, primary_key=True)
	displayName =  models.CharField(max_length=100)
	host = models.CharField(max_length=100)
	profileUrl = models.CharField(max_length=100)
	githubUrl = models.CharField(max_length=100)

# leaving commented out because there is probably better implementations
#class Friend(models.Model):
	#author1 = models.ForeignKey(Author, on_delete=models.CASCADE)
	#author2 = models.ForeignKey(Author, on_delete=models.CASCADE)
	

class Post(models.Model):
	CONTENT_TYPES = (
		("md", "text/markdown"),
		("txt","text'plain"),
		("png","image/png;base64"),
		("jpeg","image/jpeg;base64"),
	)
	ID = models.CharField(max_length=100, primary_key=True)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	contentType = models.CharField(max_length=4, choices=CONTENT_TYPES)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	#will need to change
	content = models.CharField(max_length=1000)
	#class Meta:
		#abstract = True

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
	
	
