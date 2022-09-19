import os
from django.urls import *
from . import views
from django.views.generic import TemplateView




app_name = 'bookmark'

urlpatterns = [
    path('', views.main_page, name="homepage"),
    path('user/<username>/', views.user_page),
    path('/logout/', views.logout_page, name="logout"),
    path('/register/', views.register_page),   
    path('register/success/',TemplateView.as_view
    (template_name='registration/register_success.html')),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('save/',views.bookmark_save_page),

]