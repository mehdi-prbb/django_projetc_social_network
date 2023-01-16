from django.contrib import admin

from . models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'updated')
    search_fields = ('slug',)
    list_filter = ('updated',)
    raw_id_fields = ('user',)
    prepopulated_fields = {'slug':('body',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'body', 'post', 'created', 'is_reply')
    raw_id_fields = ('user', 'post', 'reply')