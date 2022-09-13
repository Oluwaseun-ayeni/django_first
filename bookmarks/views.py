
from email import message
from django.contrib.auth import logout,get_user_model,login
from django.http import *
from .models import *
from django.shortcuts import render,redirect
from django.contrib import messages
from bookmarks.forms import *
from verify_email.email_handler import send_verification_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token



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
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to the registered email'
            message = render_to_string('acc_active_email.html',{
                'user':user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            
            user.email_user(mail_subject,message)
            messages.success(request, ('Please Confirm your email to complete registration.'))
            
            return redirect('success/')
    else:
        form = RegistrationForm()   
    context = ( {
            'form': form
        })
    return render(request, 'registration/register.html',context)   

def activate(request,uidb64,token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token(user,token):
        user.is_active =True
        user.save() 
        login(request, user)
        message.success(request, ('Your account have been confirmed.'))
        return redirect("bookmark:homepage")

    else:
        messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('home')

def logout_page(request):
    logout(request)
    messages.info(request, 'you have successfully been logged out')
    return redirect("bookmark:homepage")

