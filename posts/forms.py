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


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        labels={
            'body':False
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].widget = forms.TextInput(attrs={'class':'form-control'})


class PostSearchForm(forms.Form):
    search = forms.CharField()