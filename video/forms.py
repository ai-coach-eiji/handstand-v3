from django import forms
from .models import VideoCloudinary
from cloudinary.forms import CloudinaryFileField
from cloudinary.forms import CloudinaryJsFileField

class VideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        self.fields['video_file'].label = 'Select'
    
    class Meta:
        model = VideoCloudinary
        fields = ['video_file']
        widgets = {
            'video_file': forms.FileInput(attrs={'accept': 'video/*'})
        }

        video_file = CloudinaryJsFileField()

        