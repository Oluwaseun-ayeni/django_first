from bookmarks.models import Bookmark
from .serializers import BookmarkSerializers
from rest_framework import viewsets


class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializers








# Create your views here.
