from django.urls import path

from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('create_user', views.create_user, name='create_user'),
    path('list_user', views.list_user, name='list_user'),
    path('search_user', views.search_user, name='search_user'),
    path('', views.index, name='index'),
]
