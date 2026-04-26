from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from cloudinary.models import CloudinaryField

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # id_user = models.IntegerField()
    bio = models.TextField(blank=True, max_length=150)
    profileimg = CloudinaryField('image', default='MemeFactory_default_profileimg_okvgn4')
    banner = CloudinaryField('image', default='realm_of_chaos_wallpaper_ultra_q6ube4')
    banner_position = models.IntegerField(default=30)
    location = models.CharField(max_length=100, blank=True)

    RELATIONSHIP_CHOICES = [
    ('0', 'None'),
    ('1', 'Single'),
    ('2', 'Mingle'),
    ('3', 'Married'),
    ('4', 'Engaged'),
    ]

    relationship = models.CharField(
        max_length=10,
        choices=RELATIONSHIP_CHOICES,
        default='0'
    )

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    # image = models.ImageField(upload_to='post_images')
    image = CloudinaryField('image')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class FavouritePost(models.Model):
    user = models.CharField(max_length=100)
    post_id = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class ReportPost(models.Model):
    reporter = models.CharField(max_length=100)
    post_id = models.CharField(max_length=100)
    reason = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reporter