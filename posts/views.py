from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from . models import Post


class PostsPageView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'posts/posts_view.html', {'posts':posts})

class PostDetailView(View):
    def get(self, request, post_id, post_slug):
        post = Post.objects.get(id=post_id, slug=post_slug)
        return render(request, 'posts/post_detail.html', {'post':post})


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        if request.user.id == post.user.id:
            post.delete()
            messages.success(request, 'Your post deleted successfully')
        else:
            messages.error(request, 'You cant delete this post')
        
        return redirect('pages:home')