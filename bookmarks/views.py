from django.template import loader
from django.http import *
from .models import *
from django.shortcuts import render

def main_page(request):
    template = loader.get_template('main_page.html')
    context= ({
        'head_title':'Django Bookmarks',
        'page_title':'Welcome to Django',
        'page_body':'Where you can store and share bookmarks!'
    })
    
    return HttpResponse(template.render(context,request))

def user_page(request, username):
    try:
        user = Users.objects.get(username=username)
    except:
        raise Http404('Requested user not found.')
    bookmarks = user.bookmark_set.all()
    # template = loader.get_template('user_page.html')
    context =({
        'username': username,
        'bookmarks': bookmarks,
    })  

    # return HttpResponse(template.render(context,request))   
    return render(request, "user_page.html",context)

# Create your views here.
