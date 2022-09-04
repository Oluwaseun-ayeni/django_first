from django.urls import *
from . import views

app_name = 'bookmarks'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('users/<username>', views.user_page),
   
    
]