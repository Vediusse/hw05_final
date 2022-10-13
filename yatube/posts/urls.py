from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit'),
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('follow/',
         views.index_follow,
         name='index_follow'),
    path('profile/<str:username>/follow/',
         views.profile_follow,
         name='profile_follow'),
    path('profile/<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'),
]
