from .models import Bookmark
from .serializers import *
from rest_framework import viewsets






class BookViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializers


