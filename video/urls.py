from django.urls import path
from . import views

app_name = 'video'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('pose/<int:video_id>', views.pose, name='pose'),
    path("setup/", views.setup, name="setup"),
    path("show_progress/", views.show_progress, name="show_progress"),
    path("pose_estimation/<int:video_id>", views.pose_estimation, name="pose_estimation"),
    path('gallery/', views.gallery, name='gallery'),
    path('delete/', views.delete, name='delete'),
]