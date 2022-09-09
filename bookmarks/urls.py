import os
from django.urls import *
from . import views



app_name = 'bookmark'

urlpatterns = [
    path('', views.main_page, name="homepage"),
    path('users/<username>', views.user_page),
    path('logout/', views.logout_page, name="logout"),
    
    
    
]