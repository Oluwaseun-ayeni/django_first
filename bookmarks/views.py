from django.contrib.auth import logout
from django.http import *
from .models import *
from django.shortcuts import render,redirect
from django.contrib import messages
from bookmarks.forms import *

def main_page(request):
    return render( request, "main_page.html")
    
    

def user_page(request, username):
    try:
        user = Users.objects.get(username=username)
    except:
        raise Http404('Requested user not found.')
    bookmarks = user.bookmark_set.all()
    context = ({
        'username': username,
        'bookmarks': bookmarks,
    })    
    return render(request, "user_page.html",context)

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)  
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return redirect('register/success/')
    else:
        form = RegistrationForm()   
    context = ( {
            'form': form
        })
    return render(request, 'registration/register.html',context)         

def logout_page(request):
    logout(request)
    messages.info(request, 'you have successfully been logged out')
    return redirect("bookmark:homepage")

