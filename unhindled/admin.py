from django.contrib import admin

from .models import Post, Author, UserProfile, Comment

admin.site.register(Post)
admin.site.register(Author)
admin.site.register(UserProfile)
admin.site.register(Comment)