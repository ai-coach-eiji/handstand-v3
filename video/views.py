import os
import io
import mediapipe as mp
import numpy as np
import cv2
from PIL import Image
import ffmpeg
import json
import time
import base64

from subprocess import check_output
from .utils import has_audio_streams

from .forms import VideoForm
from .models import VideoPost, Progress, VideoCloudinary

from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .pose import pose_function
from django.shortcuts import HttpResponse, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User

import functools
import datetime as dt

import cloudinary

@login_required
def pose(request, video_id):
    try:
        video_obj = VideoCloudinary.objects.get(id=video_id)
        print("video file url: ", video_obj.video_file.url)
        #video_obj = VideoPost.objects.get(id=video_id)
        params = {
            'panel': 'video/video/pose.mp4',
            'video': video_obj,
        }
        return render(request, 'video/pose.html', params)
    except ObjectDoesNotExist:
        return render(request, 'video/404.html')

@csrf_exempt
def home(request):
    """Base page"""
    #obj = VideoPost()
    obj = VideoCloudinary()
    #cloudinary.uploader.upload(request.FILES)
    #context = dict(direct_form = VideoForm())
    form = VideoForm(request.POST or None, request.FILES or None, instance=obj)
    params = {
        'panel': 'video/video/home.mp4',
        'form': form,
    }

    if request.is_ajax():
        if form.is_valid():
            if request.user.is_authenticated:
                video_from_form = form.save()
                print("video_from_form: ", video_from_form)
                uploaded_video = VideoCloudinary.objects.get(video_file=video_from_form)#, user=request.user)
                #uploaded_video = VideoPost.objects.get(video_file=video_from_form)
                video_url = uploaded_video.video_file.url
                print("\nuploaded video URL: ", video_url)
                
                uploaded_video.user = request.user
                uploaded_video.save(update_fields=['user'])
                print("request user: ", request.user)

                #video_name = uploaded_video.video_file.name # Same file #debug mode
                video_root = uploaded_video.video_file.name # root path (MEDIA_URL + user_directory_path() in models)
                video_name = video_root.rsplit("/", 1)[1]

                #cap = cv2.VideoCapture(os.path.join(settings.MEDIA_ROOT, video_name))
                cap = cv2.VideoCapture(video_url)
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                fourcc = cv2.VideoWriter_fourcc(*'avc1')

                now = dt.datetime.now()
                time = now.strftime('%Y%m%d-%H%M%S')

                #thumbnail_name = video_name.rsplit(".", 1)[0] + '_{}'.format(time) + '.png' # debug mode
                thumbnail_name = '{}_{}.jpg'.format(video_name, time)
                #thumbnail_path = os.path.join("thumbnail", thumbnail_name)
                #dst_path = os.path.join(settings.MEDIA_ROOT, thumbnail_name)
                #dst_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), thumbnail_name)
                
                ret, image = cap.read()
                if not ret:
                    print("no ret")
                    return HttpResponse("No frame error.")
                
                if ret==True:
                    #print("\nthumbnail path: ", dst_path)
                    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb_img)
                    img = io.BytesIO() # Creating an empty instance (expand on memory)
                    pil_img.save(img,"JPEG") # Save the PIL in the empty instance as jpeg file
                    bytes_img = img.getvalue() # Get its binary source

                    print("user id: ", uploaded_video.user.id)
                    #thumbnail_dest = 'media/thumbnails/{}/{}'.format(uploaded_video.user.id, thumbnail_name)
                    thumbnail_dest = 'media/thumbnails/{}/'.format(uploaded_video.user.id)
                    print("thumbnail dest: ", thumbnail_dest)

                    thumbnail_url = cloudinary.uploader.upload(bytes_img, folder=thumbnail_dest, resource_type='image')['secure_url'] # front end URL
                    display_url = cloudinary.CloudinaryImage(str(thumbnail_url)).build_url()
                    print("generated: ", display_url)
                    #cv2.imwrite(dst_path, image)
                    #thumbnail_img = cloudinary.CloudinaryImage(thumbnail_name)
                    uploaded_video.thumbnail = display_url#thumbnail_url # assign the generated URL after the Upload (not 'secure_url' itself)
                    print("thumbnail URL: ", uploaded_video.thumbnail)

                    
                    #uploaded_video.thumbnail = thumbnail_name
                    uploaded_video.save(update_fields=['thumbnail'])
                    print("Thumbnail saved.")
                
                return JsonResponse({'message': 'OK!'})
            else:
                return JsonResponse({'message': 'You are not logged in!'})        
            
    return render(request, 'video/home.html', params)

@login_required
def gallery(request):
    try:
        all_videos = VideoCloudinary.objects.filter(user=request.user).all().order_by('-id')
        #all_videos = VideoPost.objects.filter(user=request.user).all().order_by('-id')
        params = {
            'all_videos': all_videos,
        }
        return render(request, 'video/gallery.html', params)
    except ObjectDoesNotExist:
        return render(request, 'video/404.html')

def setup(request):
    """Create a progress management instance"""
    progress = Progress.objects.create()
    return HttpResponse(progress.pk)

def show_progress(request):
    """Run the function"""
    if "progress_pk" in request.GET:
        # Process when progress_pk is specified
        progress_pk = request.GET.get("progress_pk")
        progress = get_object_or_404(Progress, pk=progress_pk)
        percent = str(int(progress.now / progress.total * 100)) + "%"
        return render(request, "video/progress_bar.html", {"percent": percent})
    else:
        return HttpResponse("Error")

def make_progress(pk):
    """Proceed with the progress associated with the primary key"""
    progress = get_object_or_404(Progress, pk=pk)
    progress.now += 1
    progress.save()

def set_argument(pk):
    """Fix the argument"""
    return functools.partial(make_progress, pk=pk)

@login_required
def do_something(request, video_id):
    """時間のかかる関数を実行する"""
    if "progress_pk" in request.GET:
        progress_pk = request.GET.get("progress_pk")
        
        video_obj = VideoCloudinary.objects.get(id=video_id)
        #video_obj = VideoPost.objects.get(id=video_id)
        video_name = video_obj.video_file.name

        input_video = video_obj.video_file.url
        #input_video = os.path.join(settings.MEDIA_ROOT, video_name)
        audio_flag = has_audio_streams(input_video)
        print("\naudio: ", audio_flag)

        now = dt.datetime.now()
        time_now = now.strftime('%Y%m%d-%H%M%S')

        #thumbnail_path = "thumbnail/" + video_name.rsplit(".", 1)[0] + '_{}'.format(time_now) + '.png'
        thumbnail_path = 'media/thumbnails/{}/'.format(video_obj.user.id)
        print("thumbnail path: ", thumbnail_path)

        #dst_path = video_name.rsplit(".", 1)[0] + '_{}'.format(time_now) + '.mp4'
        #output = os.path.join(settings.MEDIA_ROOT, dst_path)
        output = 'media/videos/{}/'.format(video_obj.user.id)
        print("output path: ", output)

        display_url, video_url = pose_function(set_argument(progress_pk), input_video, output, thumbnail_path, audio_flag)

        result_id = None
        
        #estimated_video = VideoPost(video_file=video_file, thumbnail=thumbnail_path, is_estimated=True, user=request.user)
        estimated_video = VideoCloudinary(
            video_file=video_url, 
            thumbnail=display_url, 
            is_estimated=True, 
            user=request.user
        )
        estimated_video.save()
        result_id = estimated_video.id

        #result_video = VideoPost.objects.get(id=result_id)
        result_video = VideoCloudinary.objects.get(id=result_id)
        video_obj.delete()
        
        return render(request, "video/result.html", {'result_video': result_video})
    else:
        return HttpResponse("Error")

@login_required
def delete(request):
    if request.method == 'GET':
        video_id = request.GET['video_id']
        video_obj = VideoCloudinary.objects.filter(user=request.user).get(id=video_id)
        #video_obj = VideoPost.objects.filter(user=request.user).get(id=video_id)
        video_obj.delete()

        return JsonResponse({'video_id': video_id})
    else:
        return JsonResponse({'status': 'cannot delete'})