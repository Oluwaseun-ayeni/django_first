from rest_framework import serializers
from bookmarks.models import *

class BookmarkSerializers(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = [
            'title',
            'user',
            'link',
        ]