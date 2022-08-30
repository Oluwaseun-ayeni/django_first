from django.urls import *
from . import views

app_name = 'bookmarks'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('<username>/user_page/', views.user_page, name= 'user_page'),
    
]