from django import forms

from . models import Post, Comment


class CreateUpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('body',)


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body' : forms.Textarea(attrs={'class':'form-control'})
        }