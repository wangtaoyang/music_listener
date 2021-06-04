"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.urls.conf import include
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', views.login),
    path('hello',views.hello),
    # path('fresh',views.refresh),
    # path(r'^hello/(\w+)/',views.refresh),
    path('register',views.register),
    path('superadmin',views.superadmin),
    path('get_song',views.get_song),
    path('create_playlist',views.create_playlist),
    re_path('playlist/(?P<p_id>\d+)',views.playlist),
    path('delete_song',views.delete_song),
    path('delete_playlist',views.delete_playlist),
    path('add_song',views.add_song),
    path('comments',views.comments),
    path('make_comments',views.make_comments),
    path('set_recommend',views.set_recommend),
    path('delete_comments',views.delete_comments),
    path('drop_song',views.drop_song),
    path('new_song',views.new_song),
    path('delete_user',views.delete_user)
    ]

