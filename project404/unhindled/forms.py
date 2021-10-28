from django import forms

class FriendRequestForm(forms.Form):
    adressee = forms.CharField(label='', max_length=100)
