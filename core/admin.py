from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount
from .models import ReportPost

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
@admin.register(ReportPost)
class ReportPostAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'post_id', 'reason', 'created_at')