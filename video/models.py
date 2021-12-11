from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video

from PIL import Image
import numpy as np
import os

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'videos/{0}/{1}'.format(instance.user.id, filename)

class VideoPost(models.Model):
    video_file = models.FileField()
    thumbnail = models.ImageField(upload_to='thumbnail/', blank=True, null=True)
    is_estimated = models.BooleanField(default=False)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.video_file.name)


class Progress(models.Model):
    """Progress Management Model"""
    now = models.IntegerField("Current progress", default=0)
    total = models.IntegerField("Total number of steps", default=100)

class VideoCloudinary(models.Model):
    video_file = models.FileField(upload_to=user_directory_path, blank=True, storage=VideoMediaCloudinaryStorage(),
                              validators=[validate_video])
    thumbnail = models.ImageField(blank=True, null=True)  # no need to set storage, field will use the default one
    is_estimated = models.BooleanField(default=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.video_file.name)