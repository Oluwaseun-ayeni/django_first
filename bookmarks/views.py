from django.contrib.auth import logout
from django.http import *
from .models import *
from django.shortcuts import render,redirect
from django.contrib import messages
from django.template import RequestContext

def main_page(request):
    return render( request, "main_page.html")
    
    

def user_page(request, username):
    try:
        user = Users.objects.get(username=username)
    except:
        raise Http404('Requested user not found.')
    bookmarks = user.bookmark_set.all()
    variables = RequestContext(request,{
        'username': username,
        'bookmarks': bookmarks,
    })    
    return render(request, "user_page.html",variables)

    

def logout_page(request):
    logout(request)
    messages.info(request, 'you have successfully been logged out')
    return redirect("bookmark:homepage")

