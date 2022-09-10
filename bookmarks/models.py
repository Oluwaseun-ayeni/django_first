from django.db import models

class Link(models.Model):
    url = models.URLField(unique=True)

class Users(models.Model):
    username = models.CharField( max_length=40)
    password = models.CharField( max_length=200) 
    email = models.EmailField(max_length=75)

class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)   

