from django.urls import path

from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('create_user', views.create_user, name='create_user'),
    path('user_login', views.user_login, name='user_login'),
    path('user_detail', views.user_detail, name='user_detail'),
    path('list_user', views.list_user, name='list_user'),
    path('search_user', views.search_user, name='search_user'),
    path('update_user', views.update_user, name='update_user'),
    path('', views.index, name='index'),
]
