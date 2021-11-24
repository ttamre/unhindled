from django import forms
from django.db import models
from .models import Comment, User
from django.contrib.auth.forms import UserCreationForm

class FormComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields =('comment',)

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']