from email import message
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
from django.contrib.auth.decorators import login_required,permission_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


 

def main_page(request):
    shared_bookmarks = SharedBookmark.objects.order_by(
        '-date'
    )[:10]
    context =({
        'shared_bookmarks': shared_bookmarks
    })
    return render( request, "main_page.html", context)



def login_page(request):

    if request.method == 'POST':
        password = request.POST.get('password')
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Username OR Password not Valid')

    context = {}
    return render(request, 'registration/login.html', context)



ITEM_PER_PAGE = 10    
def user_page(request, username):
    user = get_object_or_404(User,username=username)
    query_set = user.bookmark_set.order_by('-id')
    paginator = Paginator(query_set, ITEM_PER_PAGE)
    is_friend = Friendship.objects.filter(
        from_friend = request.user.id,
        to_friend=user
    )

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = ({
        'username': username,
        'show_tags': True,
        'show_edit': username == request.user.username,
        'page_obj' : page_obj,
        'is_friend' : is_friend,
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
            if 'invitation' in request.session:
                invitation = \
                    Invitation.objects.get(id=request.session['invitation'])
                friendship = Friendship(
                    from_friend=user,
                    to_friend=invitation.sender
                )
                friendship.save()
                invitation.delete()
                del request.session['invitation']
            current_site = get_current_site(request)
            subject = 'Activation link has been sent to the registered email'
            message = render_to_string('acc_active_email.html',{
                'user':user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            recipient_list = [user.email, ]
            email_from = settings.EMAIL_HOST_USER

            send_mail(subject,message, email_from,recipient_list)
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


# @permission_required('bookmarks.add_bookmark', login_url="/login/")
@login_required
def bookmark_save_page(request):
    ajax = 'ajax' in request.GET
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            bookmark = _bookmark_save(request,form)
            if ajax:
                context =({
                    'bookmarks': [bookmark],
                    'show_edit': True,
                    'show_tags': True
                })
                return render(request, 'bookmark_list.html', context)
            else:
                return HttpResponseRedirect('/user/%s/' % request.user.username)
        else:
            if ajax:
                return HttpResponse('failure')
        
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
    if ajax:
        return render(request, 'bookmark_save_form.html' ,context)
    else:
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
    if form.cleaned_data['share']:
        shared_boomark, created = SharedBookmark.objects.get_or_create(
            bookmark=bookmark
        )
        if created:
            shared_boomark.users_voted.add(request.user)
            shared_boomark.save()
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
            keywords = query.split()
            q = Q()
            for keyword in keywords:
                q = q & Q(title__icontains=keyword)
            form = SearchForm({'query' : query})
            bookmarks = Bookmark.objects.filter(q)[:10]
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

@login_required   
def bookmark_vote_page(request):
    if 'id' in request.GET:
        try:
            id = request.GET['id']
            shared_bookmark = SharedBookmark.objects.get(id=id)
            user_voted = shared_bookmark.users_voted.filter(
                username=request.user.username
            )
            if not user_voted:
                shared_bookmark.votes += 1
                shared_bookmark.users_voted.add(request.user)
                shared_bookmark.save()
        except ObjectDoesNotExist:
            raise Http404('Bookmark not found.')
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    return redirect('/')


def popular_page(request):
    today = datetime.today()
    yesterday = today - timedelta(1)
    shared_bookmarks = SharedBookmark.objects.filter(
        date__gt=yesterday
    )
    shared_bookmarks = shared_bookmarks.order_by(
        '-votes'
    )[:10]

    context = ({
        'shared_bookmarks': shared_bookmarks,
    })
    return render(request, 'popular_page.html', context)

def bookmark_page(request,bookmark_id):
    shared_bookmark = get_object_or_404(SharedBookmark,
            id=bookmark_id)
    context = ({
        'shared_bookmark': shared_bookmark
    })

    return(request, 'bookmark_page.html', context)

def friends_page(request, username):
    user = get_object_or_404(User, username=username)
    friends = \
        [friendship.to_friend for friendship in user.friend_set.all()]
    friend_bookmarks = \
        Bookmark.objects.filter(user__in=friends).order_by('-id')
    context = ({
        'username' : username,
        'friends' : friends,
        'bookmarks' : friend_bookmarks[:10],
        'show_tags' : True,
        'show_user' : True
    })
    return render(request, 'friends_page.html', context)

@login_required
def friend_add(request):
    if 'username' in request.GET:
        friend = \
            get_object_or_404(User, username=request.GET['username'])
        friendship = Friendship(
            from_friend = request.user,
            to_friend = friend
        )
        try:
            friendship.save()
            messages.success(request,
                '%s was added to your friend list.' % friend.username
            )
        except:
            messages.success(request,
                '%s is already a friend of yours.' % friend.username
            )
        return redirect('/friends/%s/' % request.user.username)
    else:
        raise Http404


@login_required(login_url='/login/')
def friend_invite(request):
    if request.method == 'POST':
        form = FriendInviteForm(request.POST)
        if form.is_valid():
            current_user = auth.get_user(request)
            invitation = Invitation(
                name = form.cleaned_data['name'],
                email = form.cleaned_data['email'],
                code = User.objects.make_random_password(20),
                sender = current_user
            )
            invitation.save()
            try:
                invitation.send()
                messages.success(request,
                    _('An invitation was sent to %(email)s.') % {'email':invitation.email}
                )
            except:
                messages.success(request,
                   _('There was an error while sending this invitation.')
                )
            return redirect('/friend/invite/')
    else:
        form = FriendInviteForm()
    context = ({
        'form' : form
    })
    return render(request, 'friend_invite.html', context)


def friend_accept(request,code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    request.session['invitation'] = invitation.id
    return redirect('/register')


def logout_page(request):
    logout(request)
    messages.info(request, 'you have successfully been logged out')
    return redirect("bookmark:homepage")

