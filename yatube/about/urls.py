from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('tech/', views.Tech.as_view(), name='tech'),
    path('author/', views.Author.as_view(), name='author'),
]
