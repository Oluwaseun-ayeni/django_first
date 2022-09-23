from rest_framework import serializers
from .models import *

class BookmarkSerializers(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = [
            'title',
            'user',
            'link',
        ]