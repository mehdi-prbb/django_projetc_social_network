from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostsPageView.as_view(), name='posts_list'),
    path('<int:post_id>/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('delete/<int:post_id>/', views.PostDeleteView.as_view(), name='post_delete'),
]
