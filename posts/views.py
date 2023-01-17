from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from . models import Post, Comment, Like
from . forms import CreateUpdatePostForm, CommentCreateForm, CommentReplyForm


class PostsPageView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'posts/posts_view.html', {'posts':posts})

class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomments.filter(is_reply=False)
        can_like = False
        if request.user.is_authenticated and self.post_instance.user_can_like(request.user):
            can_like = True
        return render(request, 'posts/post_detail.html', {
            'post':self.post_instance,
            'comments':comments,
            'form':self.form_class,
            'form_reply':self.form_class_reply,
            'can_like':can_like,
            })
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, 'Your comment submitted successfully')
            return redirect('posts:post_detail', self.post_instance.id, self.post_instance.slug)


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


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['post_id'])
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        form = self.form_class(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request, 'your reply is submitted successfully.')
        return redirect('posts:post_detail', post.id, post.slug)



class PostLikeDislikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(post=post, user=request.user)

        if like.exists():
            like.delete()
            messages.success(request, 'you have already disliked this post.')
        else:
            Like.objects.create(post=post, user=request.user)
            messages.success(request, 'you liked this post.')
        return redirect('posts:post_detail', post.id, post.slug)


    