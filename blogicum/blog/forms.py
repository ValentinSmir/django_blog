from django import forms
from django.contrib.auth.models import User

from blog.models import Comment, Post

# Спасибо за ревью!


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date',
                  'location', 'category',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
