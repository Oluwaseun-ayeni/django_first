from django.contrib import admin
from .models import *

admin.site.register(Bookmark)
admin.site.register(User)
admin.site.register(Link)
admin.site.register(Tag)

# Register your models here.
