from django import forms

from . models import Post


class CreateUpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('body',)