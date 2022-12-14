from django.contrib import admin
from .models import *


admin.site.register(Link)
admin.site.register(Tag)
admin.site.register(Invitation)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'user') 
    list_filter = ('user', )
    ordering = ('title', )
    search_fields = ('title', )

# Register your models here.
