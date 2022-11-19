from django.urls import path

from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('create-user', views.create_user, name='create_user'),
    path('login-user', views.user_login, name='user_login'),
    path('detail/<str:account>', views.user_detail, name='user_detail'),
    path('list-all-users', views.list_user, name='list_user'),
    path('search-user', views.search_user, name='search_user'),
    path('update-user', views.update_user, name='update_user'),
    path('delete-user/<str:account>', views.delete_user, name='delete_user'),
    path('', views.index, name='index'),
]
