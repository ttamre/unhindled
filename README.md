# CMPUT404 Project


## Quick Links
* [App](https://dashboard.heroku.com/apps/unhindled)
* [OpenAPI Documentation](https://unhindled.herokuapp.com/redoc/)
* [Project Requirements](https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/project.org)

## Commands
**Create user**
```bash
python3 manage.py createsuperuser
# create credentials, then log in
```
**Create Postgres DB**
```
CREATE DATABASE unhindled;
```


## Team Members
NAME | CCID
---- | ---- 
Ismaeel Mohiuddin|ismaeel
Tem Tamre|ttamre
Thomas Pham|tpham3
Joshua Smith|jds1
Zoey Pu|jpu1


## Reference
* Legion Script: https://www.youtube.com/watch?v=XBMatmjS5yM&t=1576s
* Abhishek Verma: https://www.youtube.com/watch?v=An4hW4TjKhE
* Table CSS: https://www.w3schools.com/css/tryit.asp?filename=trycss_table_fancy
* Abhishek Verma: https://www.youtube.com/watch?v=An4hW4TjKhE
* Will Vincent: https://learndjango.com/tutorials/django-login-and-logout-tutorial
* Will Vincent: https://learndjango.com/tutorials/django-signup-tutorial
* Richard Yen: https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django
* Adeyemi Atoyegbe: https://www.section.io/engineering-education/django-app-using-postgresql-database/
* Mitchel Cabuloy: https://mitchel.me/slippers/docs/getting-started/
* W3 School: https://www.w3schools.com/howto/howto_css_dropdown.asp
* Geeksforgeeks: https://www.geeksforgeeks.org/basic-authentication-django-rest-framework/
* Django REST Framework: https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
* Checking array elements safely https://stackoverflow.com/questions/28263773/safe-way-to-check-if-array-element-exists
* Safe variable passing from Django to DOM https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#json-script
* Python dict comprehension: https://discuss.python.org/t/copy-a-dictionary-except-some-keys/2559/3
* Basic tooltip: https://www.w3schools.com/css/css_tooltip.asp

## Completed User Stories
s an author I want to make public posts.
As an author I want to edit public posts.
As an author, posts I create can link to images.
As an author, posts I create can be images.
As a server admin, images can be hosted on my server.
As an author, posts I create can be private to another author
As an author, posts I create can be private to my friends
As an author, I can share other author’s public posts
As an author, posts I make can be in simple plain text
As an author, posts I make can be in CommonMark
As an author, I want a consistent identity per server
As a server admin, I want to host multiple authors on my server
As a server admin, I want to share public images with users on other servers.
As an author, I want to pull in my github activity to my “stream”
As an author, I want to post posts to my “stream”
As an author, I want to delete my own public posts.
As an author, I want to befriend local authors
As an author, I want to befriend remote authors
As an author, I want to feel safe about sharing images and posts with my friends – images shared to friends should only be visible to friends. [public images are public]
As an author, when someone sends me a friends only-post I want to see the likes.
As an author, I want un-befriend local and remote authors
As an author, I want to be able to use my web-browser to manage my profile
As an author, I want to be able to use my web-browser to manage/author my posts
As a server admin, I want to be able add, modify, and remove authors.
As a server admin, I want to OPTIONALLY be able allow users to sign up but require my OK to finally be on my server
As a server admin, I don’t want to do heavy setup to get the posts of my author’s friends.
As a server admin, I want a restful interface for most operations
As an author, other authors cannot modify my public post
As an author, other authors cannot modify my shared to friends post.
As an author, I want to comment on posts that I can access
As an author, I want to like posts that I can access
As an author, my server will know about my friends
As an author, When I befriend someone it follows them, only when the other authors befriends me do I count as a real friend.
As an author, I want to know if I have friend requests.
As an author I should be able to browse the public posts of everyone
As a server admin, node to node connections can be authenticated with HTTP Basic Auth
As an author, I want to be able to make posts that are unlisted, that are publicly shareable by URI alone (or for embedding images)
