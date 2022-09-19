from django.db import models
# from django.contrib.auth.models import User





class Link(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

class Users(models.Model):
    username = models.CharField( max_length=40)
    password = models.CharField( max_length=200) 
    email = models.EmailField(max_length=75)   
    
    def is_active(self):
        return True

class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(Users, related_name="bookmarks",on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)  

    def __str__(self):
        return '%s, %s' % (self.user.username, self.link.url)

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    bookmarks = models.ManyToManyField(Bookmark)
    
    def __str__(self):
        return self.name

