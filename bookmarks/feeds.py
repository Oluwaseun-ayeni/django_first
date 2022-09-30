from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User


class RecentBookmarks(Feed):
    def get_object(self,bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return User.objects.get(username=bits[0])
   

    def link(self, user):
        return '/feeds/user/%s/' % user.username

    def title(self,user):
        return 'Django Bookmarks | Bookmarks for %s' % user.username
    
    def description(self, user):
        return 'Recent bookmarks posted by %s' % user.username

    def items(self,user):
        return user.bookmark_set_order_by('-id')[10]