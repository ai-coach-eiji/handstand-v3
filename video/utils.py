import cv2
import time
import os
import mediapipe as mp
import numpy as np
import ffmpeg
from subprocess import check_output
import json

from django.conf import settings


def has_audio_streams(file_path):
  command = ['ffprobe', '-show_streams',
           '-print_format', 'json', file_path]
  output = check_output(command)
  parsed = json.loads(output)
  streams = parsed['streams']
  audio_streams = list(filter((lambda x: x['codec_type'] == 'audio'), streams))
  return len(audio_streams) > 0

