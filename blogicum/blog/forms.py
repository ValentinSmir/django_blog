from django import forms

from .models import Comment, Post

from django.contrib.auth.models import User


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
