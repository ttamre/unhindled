from django import forms
from django.db import models

from unhindled.connect import get_foreign_authors_list
from .models import Comment, Post, User
from django.contrib.auth.forms import UserCreationForm

class FormComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields =('comment',)

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        choices = []
        local_author = User.objects.all()
        for user in local_author:
            data = str(user.id)
            human_text = user.username
            choices.append((data, human_text))

        foreign_authors = get_foreign_authors_list()
        for author in foreign_authors:
            if "unhindled.herokuapp.com" not in author["host"]:
                data = author["id"]
                human_text = author["displayName"] + " from " + author["host"]
                choices.append((data, human_text))

        self.fields['send_to'] = forms.ChoiceField(choices=choices)
