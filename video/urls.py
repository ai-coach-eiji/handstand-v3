from django.urls import path
from . import views
#from django.contrib.auth import views as auth_views
#from .views import SignUpView

app_name = 'video'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('pose/<int:video_id>', views.pose, name='pose'),
    path("setup/", views.setup, name="setup"),
    path("show_progress/", views.show_progress, name="show_progress"),
    path("do_something/<int:video_id>", views.do_something, name="do_something"),
    path('gallery/', views.gallery, name='gallery'),
    path('delete/', views.delete, name='delete'),
]