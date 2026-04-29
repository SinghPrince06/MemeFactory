from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from django.http import JsonResponse
from core.models import Profile
from itertools import chain
from .models import FavouritePost, ReportPost
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404
# Create your views here.

@login_required
def index(request):
    print(request.user)
    print(request.user.is_authenticated)
    user = request.user.username

    user_object = User.objects.get(username=user)
    user_profile = Profile.objects.get(user=user_object)

    following = FollowersCount.objects.filter(
        follower=user
    ).values_list('user', flat=True)

    fav = FavouritePost.objects.filter(user=user).first()
    user_favourite_post_id = fav.post_id if fav else None

    posts = Post.objects.all().order_by('-created_at')

    if user_favourite_post_id:
        posts = posts.annotate(
            is_fav=Case(
                When(id=user_favourite_post_id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('is_fav', '-created_at')

    posts = list(posts)

    for post in posts:
        post.author_profile = Profile.objects.filter(user__username=post.user).first()

    suggestions = Profile.objects.exclude(
        user__username=user
    )[:6]


    return render(request, 'index.html', {
        'user_profile': user_profile,
        'posts': posts,
        'suggestions_username_profile_list': suggestions,
        'following_users': following,
        'user_favourite_post_id': user_favourite_post_id,
    })

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('upload_image')
        caption = request.POST['caption']

        #stops empty posts
        if image is None:
            return redirect('/')   # or show error message

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else : 
        return redirect('/')

@login_required(login_url='signin')
def delete_post(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        user = request.user.username

        post = Post.objects.get(id=post_id)

        if post.user == user:
            post.delete()
            messages.success(request, "Post deleted")

    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1
        post.save()
        liked = True
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        liked = False

    return JsonResponse({
        'likes': post.no_of_likes,
        'liked': liked
    })

@login_required(login_url='signin')
def favourite_post(request):
    if request.method == 'POST':
        user = request.user.username
        post_id = request.POST.get('post_id')

        fav = FavouritePost.objects.filter(user=user).first()

        if fav:
            if fav.post_id == post_id:
                fav.delete()
                messages.success(request, "Favourite removed")
            else:
                fav.post_id = post_id
                fav.save()
                messages.success(request, "Favourite post changed")
        else:
            FavouritePost.objects.create(user=user, post_id=post_id)
            messages.success(request, "Favourite added")

    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='signin')
def report_post(request):
    if request.method == "POST":
        reporter = request.user.username
        post_id = request.POST.get('post_id')
        reason = request.POST.get('reason', '').strip()

        if len(reason) < 10:
            messages.error(request, "Reason must be at least 10 characters")
            return redirect(request.META.get('HTTP_REFERER'))

        if len(reason) > 100:
            messages.error(request, "Reason cannot exceed 100 characters")
            return redirect(request.META.get('HTTP_REFERER'))

        existing = ReportPost.objects.filter(
            reporter=reporter,
            post_id=post_id
        ).first()

        if existing:
            messages.error(request, "You already reported this post")
            return redirect(request.META.get('HTTP_REFERER'))

        ReportPost.objects.create(
            reporter=reporter,
            post_id=post_id,
            reason=reason
        )

        total_reports = ReportPost.objects.filter(post_id=post_id).count()

        if total_reports >= 10:
            post = Post.objects.filter(id=post_id).first()
            if post:
                post.delete()

        messages.success(request, "Report sent")

    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
        
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']

        next_url = request.POST.get('next', '/')

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            FollowersCount.objects.create(follower=follower, user=user)

        return redirect(next_url)

    return redirect('/')
    
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        user_profile.bio = request.POST.get('bio')
        user_profile.location = request.POST.get('location')
        user_profile.relationship = request.POST.get('relationship')

        # Profile image
        if request.FILES.get('image'):
            user_profile.profileimg = request.FILES.get('image')

        # ✅ ADD THIS (banner)
        if request.FILES.get('banner'):
            user_profile.banner = request.FILES.get('banner')

        user_profile.save()
        return redirect('profile', pk=request.user.username)

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('password2')

        if not username or not email or not password or not confirmpassword:
            messages.info(request, "All fields are required")
            return redirect('signup')
        
        if len(username) < 3:
            messages.info(request, "Username too short")
            return redirect('signup')

        if password == confirmpassword:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email is already in use!")
                return redirect('signup')
            
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username is not available!")
                return redirect('signup')
            else : 
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

            #log user in and redirect to settings page
            user_login = auth.authenticate(username=username, password=password)
            auth.login(request, user_login)

            #create a profile object for the new user

            new_profile = Profile.objects.get_or_create(user=user)
            return redirect('settings')
        else : 
            messages.info(request, "Password Doesn't Match")
            return redirect('signup')
    else : 
        return render(request, 'signup.html')

def signin(request):
    print("SIGNIN HIT")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'User does not exist, please register first!')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def search(request):
    username = request.GET.get('username')

    users = User.objects.filter(username__icontains=username)
    profiles = Profile.objects.filter(user__in=users)

    return render(request, 'search.html', {'profiles': profiles})


@login_required(login_url='signin')
def search_ajax(request):
    query = request.GET.get('q')

    users = User.objects.filter(username__icontains=query)[:6]

    data = []
    for user in users:
        profile = Profile.objects.get(user=user)
        data.append({
            'username': user.username,
            'image': profile.profileimg.url
        })

    return JsonResponse(data, safe=False)

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

