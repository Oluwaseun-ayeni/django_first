
from django.urls import *
from . import views
from django.views.generic import TemplateView






app_name = 'bookmark'


urlpatterns = [
    path('', views.main_page, name="homepage"),
    path('user/<username>/', views.user_page, name="userpage"),
    path('logout/', views.logout_page, name="logout"),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page),   
    path('register/success/',TemplateView.as_view
    (template_name='registration/register_success.html'),name='success'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('save/',views.bookmark_save_page),
    path('tag/<tag_name>', views.tag_page),
    path('tag/' ,views.tag_cloud_page), 
    path('search/', views.search_page),
    path('vote/', views.bookmark_vote_page),
    path('popular/', views.popular_page),
    path('bookmark/<int:bookmark_id>', views.bookmark_page),
]







