from django.contrib import admin
from .models import VideoPost, VideoCloudinary

# Register your models here.
admin.site.register(VideoPost)
admin.site.register(VideoCloudinary)