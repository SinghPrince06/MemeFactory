from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('signin/', views.signin, name='signin'),
    path('ping/', views.ping),
    path('post/<uuid:id>/', views.post_detail, name='post_detail'),
    path('settings/', views.settings, name='settings'),
    path('upload/', views.upload, name='upload'),
    path('delete-post/', views.delete_post, name='delete_post'),
    path('report-post/', views.report_post, name='report_post'),
    path('favourite/', views.favourite_post, name='favourite'),
    path('follow/', views.follow, name='follow'),
    path('search/', views.search, name='search'),
    path('search-ajax/', views.search_ajax, name='search_ajax'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('like-post/', views.like_post, name='like-post'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
