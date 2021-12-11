import time
import os
import io
import csv
import copy
import itertools
from collections import deque
import tempfile

import mediapipe as mp
import cv2
from PIL import Image
import numpy as np
import ffmpeg
#import tensorflow as tf

from ffpyplayer.player import MediaPlayer

from django.conf import settings

import cloudinary

'''class PoseLstm(object):
    def __init__(
        self,
        model_path=os.path.join(settings.BASE_DIR, 'video/model/weight1_lstm3.tflite'),
        num_threads=1,
    ):
        self.interpreter = tf.lite.Interpreter(model_path=model_path,
                                               num_threads=num_threads) # model reading

        self.interpreter.allocate_tensors() # memory space (required)
        self.input_details = self.interpreter.get_input_details() # input layer details
        self.output_details = self.interpreter.get_output_details() # output layer details

    def __call__(self, pose_lstm_coords):
        input_data = np.array(pose_lstm_coords, dtype=np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data) # set to interpreter
        self.interpreter.invoke() # run prediction

        result = self.interpreter.get_tensor(self.output_details[0]['index']) # get the output
        result_index = np.argmax(result[0])

        return result_index'''

def extract_keypoints(image, results):
    image_width, image_height = image.shape[1], image.shape[0]
    
    landmark_list = []
    for res in results.pose_landmarks.landmark:
        x = min(int(res.x * image_width), image_width - 1)
        y = min(int(res.y * image_height), image_height - 1)
        landmark_list.append([x, y])
    return landmark_list

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to 1D list
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))
    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list

def pose_function(make_progress_func, input_video, dst, thumbnail_path, audio_flag):
    """Processing running behind the scenes."""
    cap = cv2.VideoCapture(input_video)
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    total_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    #total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("total frame: ", total_frame)

    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'avc1')

    actions = np.array(['entry', 'swing', 'straight'])
    sequence_length = 15
    pose_lstm_coords = deque(maxlen=sequence_length)

    display_url, video_url = None, None
    
    with tempfile.TemporaryDirectory() as dname:
        print("一時ディレクトリ名: ", dname)
        print("一時ディレクトリが作成されたかを確かめる: ", os.path.exists(dname)) # True
        #with open(os.path.join(dname, "test.txt"), "w") as f:
            #print("test", file=f)

        #output_path = dst+'test.mp4'
        output_path = dname+'/estimated.mp4'
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        with mp_pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:

            # Pre-trained model of LSTM (handstand)
            #pose_lstm = PoseLstm()

            # Create a progress list
            f_percent = [round(total_frame * i, 0) for i in np.arange(0.01, 1.01, 0.01)]
            print("f_percent: ", f_percent)

            im_counter = 0
            while (cap.isOpened()):
                frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES) + 1 # Do this to match the progress bar
                print("frame_pos: ", frame_pos)

                # Update the progress according to frame position
                if frame_pos in f_percent:
                    make_progress_func()

                ret, frame = cap.read()
                if not ret:
                    break
                
                annotated_image = frame.copy()
                results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                if results.pose_landmarks is not None:
                    mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=results.pose_landmarks,
                    connections=mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                    )

                    # Pose coord memory
                    keypoints = extract_keypoints(annotated_image, results)
                    keypoints = pre_process_landmark(keypoints)
                    pose_lstm_coords.append(keypoints)

                    if len(pose_lstm_coords) == 15:
                        pass
                        #pose_id = pose_lstm(np.expand_dims(pose_lstm_coords, axis=0))
                        #print(actions[pose_id])
                        #cv2.putText(annotated_image, 'Pose: {}'.format(actions[pose_id]),
                            #(30, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255,255), thickness=2)
                    
                writer.write(annotated_image)
                
                if im_counter == 0:
                    #cv2.imwrite(os.path.join(settings.MEDIA_ROOT, thumbnail_path), annotated_image)
                    rgb_img = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb_img)
                    img = io.BytesIO() # Creating an empty instance (expand on memory)
                    pil_img.save(img,"JPEG") # Save the PIL in the empty instance as jpeg file
                    bytes_img = img.getvalue() # Get its binary source

                    thumbnail_url = cloudinary.uploader.upload(bytes_img, folder=thumbnail_path, resource_type='image')['secure_url'] # front end URL
                    display_url = cloudinary.CloudinaryImage(str(thumbnail_url)).build_url()
                    print("pose thumbnail: ", display_url)
                    
                im_counter += 1
        
        cap.release()
        writer.release()
        cv2.destroyAllWindows()

        # With audio source
        if audio_flag:
            print('\nThis video has audio.')

            stream = ffmpeg.input(input_video)
            audio = stream.audio

            #audio_name = "estimated_" + dst_path
            audio_name = "estimated_audio.mp4"
            #audio_absolute = os.path.join(settings.MEDIA_ROOT, audio_name)
            audio_absolute = os.path.join(dname, audio_name)

            stream_s = ffmpeg.input(output_path) # processed video(mute)
            stream_s = ffmpeg.output(stream_s, audio, audio_absolute)
            ffmpeg.run(stream_s, overwrite_output=True)

            #video_file = audio_name
            process_result = audio_absolute
        else:
            print('\nNo audio.')
            #video_file = dst_path
            process_result = output_path

        video_res = cloudinary.uploader.upload(process_result, folder=dst, resource_type="video")['secure_url']
        video_url = cloudinary.CloudinaryImage(str(video_res)).build_url()
        print("video url: ", video_url)

    print("破棄する（一時ディレクトリが存在するかどうか）: ", os.path.exists(dname))     # False

    return display_url, video_url