from rest_framework.routers import *
from bookmark_api import views
from django.urls import path,include


router = SimpleRouter()
router.register('bookmark', views.BookmarkViewSet,basename="bookmark")

urlpatterns = [
    path('', include(router.urls)),
    
]