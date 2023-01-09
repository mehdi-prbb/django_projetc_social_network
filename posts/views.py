from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.text import slugify

from . models import Post
from . forms import CreateUpdatePostForm


class PostsPageView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'posts/posts_view.html', {'posts':posts})

class PostDetailView(View):
    def get(self, request, post_id, post_slug):
        post = get_object_or_404(Post, id=post_id, slug=post_slug)
        return render(request, 'posts/post_detail.html', {'post':post})


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user.id == post.user.id:
            post.delete()
            messages.success(request, 'Your post deleted successfully')
        else:
            messages.error(request, 'You cant delete this post')
        
        return redirect('pages:home')


class PostUpdateView(LoginRequiredMixin,View):
    form_class = CreateUpdatePostForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if post.user.id != request.user.id:
            messages.error(request, 'you cant update this post')
            return redirect('pages:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'posts/post_update.html', {'form':form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST,instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(request, 'you updated post successfully')
            return redirect('posts:post_detail', new_post.id, new_post.slug)


class PostCreateView(LoginRequiredMixin, View):
    form_class = CreateUpdatePostForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'posts/post_create.html', {'form':form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'you create new post successfully')
            return redirect('posts:post_detail', new_post.id, new_post.slug)


    