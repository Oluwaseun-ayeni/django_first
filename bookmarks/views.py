from email import message
from django.contrib.auth import logout,get_user_model,login
from django.http import *
from .models import *
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from bookmarks.forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings



def main_page(request):
    return render( request, "main_page.html")
    
    

def user_page(request, username):
    user = get_object_or_404(Users,username=username)
    bookmarks = user.bookmarks_set.all()
    context = ({
        'username': username,
        'bookmarks': bookmarks,
        'show_tags': True
    })    
    return render(request, "user_page.html",context)

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)  
        if form.is_valid():
            user = Users.objects.create(
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
            recipient_list = [user.email, ]
            email_from = settings.EMAIL_HOST_USER

            send_mail(mail_subject,message, email_from,recipient_list)
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

@login_required(login_url='/login/')
def bookmark_save_page(request):
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            link, dummy = Link.objects.get_or_create(
                url=form.cleaned_data['url']
            )
            
            bookmark, created =Bookmark.objects.get_or_create(
                user=request.user.id,
                link=link
            )
            bookmark.title = form.cleaned_data['title']

            if not created:
                bookmark.tag_set.clear()

            tag_names = form.cleaned_data['tags'].split()
            for tag_name in tag_names:
                tag , dummy = Tag.objects.get_or_create(name=tag_name)
                bookmark.tag_set.add(tag)
            bookmark.save()   
            return HttpResponseRedirect('/user/%s/' % request.user.username)
    else:
        form = BookmarkSaveForm()    
    context = {
        'form':form
    }   
    return render(request, 'bookmark_save.html', context)


def logout_page(request):
    logout(request)
    messages.info(request, 'you have successfully been logged out')
    return redirect("bookmark:homepage")

