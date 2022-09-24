from email import message
from logging import raiseExceptions
from wsgiref.handlers import read_environ
from django.contrib.auth import logout,get_user_model,login,authenticate
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
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist




 

def main_page(request):
    return render( request, "main_page.html")


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user = authenticate(request, username=username,
                        password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, ('You have successfully log in'))
                return redirect("/")

        else:
            return redirect("bookmark:login")
    else:
        form = LoginForm()   
    context = ( {
            'form': form
        })
    return render(request, 'registration/login.html', context)
    
    

def user_page(request, username):
    user = get_object_or_404(User,username=username)
    bookmarks = user.bookmark_set.all()
    context = ({
        'username': username,
        'bookmarks': bookmarks,
        'show_tags': True,
        'show_edit': username == request.user.username,
    })    
    return render(request, "user_page.html",context)

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)  
        if form.is_valid():
            user = User.objects.create(
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
            bookmark = _bookmark_save(request,form)
            return HttpResponseRedirect('/user/%s/' % request.user.username)
        
    elif 'url' in request.GET:
        url = request.GET['url']
        title = ''
        tags = ''
        try:
            link = Link.objects.get(url=url)
            current_user = auth.get_user(request)
            bookmark = Bookmark.objects.get(
                link=link,
                user=current_user
            )
            title = bookmark.title
            tags = ' '.join(
                tag.name for tag in bookmark.tag_set.all()
            )
        except ObjectDoesNotExist:
            pass
        form = BookmarkSaveForm({
            'url': url,
            'title': title,
            'tags': tags
        })
    else:
        form = BookmarkSaveForm()    
    context = {
        'form':form
    }   
    return render(request, 'bookmark_save.html', context)

def _bookmark_save(request, form):
    link, dummy = \
        Link.objects.get_or_create(
                    url=form.cleaned_data['url'])
    current_user = auth.get_user(request)
    bookmark, created =Bookmark.objects.get_or_create(
        user=current_user,
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
    return bookmark  


def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    bookmarks = tag.bookmarks.order_by('-id')
    context = ({
        'bookmarks': bookmarks,
        'tag_name' : tag_name,
        'show_tag' : True,
        'show_user': True
    })
    return render(request, 'tag_page.html', context)


def tag_cloud_page(request):
    MAX_WEIGHT = 7
    tags = Tag.objects.order_by('name')
    min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
        tag.count = tag.bookmarks.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count
    range = float(max_count - min_count)
    if range == 0.0:
        range = 1.0
    for related_tag in tags:
        related_tag.weight = int(
            MAX_WEIGHT * (tag.count - min_count) / range
        )
    context = ({
        'tags': tags
    })
    return render(request, 'tag_cloud_page.html', context)


def search_page(request):
    form = SearchForm()
    bookmarks = []
    show_results = False
    
    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query' : query})
            bookmarks = \
                Bookmark.objects.filter(title__icontains=query)[:10]
    context = ({
        'form' : form,
        'bookmarks' : bookmarks,
        'show_results': show_results,
        'show_tags' : True,
        'show_user' : True
    })
    if 'ajax' in request.GET:
        return render(request,'bookmark_list.html', context)
    else:
        return render(request, 'search.html',context)
        


def logout_page(request):
    logout(request)
    messages.info(request, 'you have successfully been logged out')
    return redirect("bookmark:homepage")

