from os import listdir
from os.path import isfile, join
import time
import json
import cv2
from functools import partial

import logging
logging.basicConfig(level=logging.INFO)

from obswebsocket import obsws, requests

host = "localhost"
port = 4444

print = partial(print, flush=True)

currently_in_default_scene = False
def execute_tick(video_capture, image_files_to_search_for, obs, default_scene_name, target_scene_name):
    global currently_in_default_scene
    try:
        ret, frame = video_capture.read()
        
        if frame_contains_one_or_more_matching_images(frame, image_files_to_search_for):
            if currently_in_default_scene:
                obs.call(requests.SetCurrentScene(target_scene_name))
                currently_in_default_scene = False
        elif not currently_in_default_scene:
            obs.call(requests.SetCurrentScene(default_scene_name))
            currently_in_default_scene = True
    except Exception as e:
        print(e)

def get_valid_camera_indices():
    # checks the first 10 indexes.
    index = 0
    arr = []
    max_to_check = 10
    while index <= max_to_check:
        cap = cv2.VideoCapture(index)
        ret, frame = cap.read()
        if ret:
            arr.append(index)
            cap.release()
        index += 1
    indices_cache = arr
    return indices_cache

def frame_contains_one_or_more_matching_images(frame, image_files_to_search_for):
    if frame is not None:
        for image in image_files_to_search_for:
            result = cv2.matchTemplate(frame.copy(), image, cv2.TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            print(min_val)
            if min_val < 0.01:
                return True
    return False

def main():
    with open("obs_screen_recognition_settings.json") as settings_file:
        application_settings = json.load(settings_file)

    print("Running with settings:", application_settings)
    image_directory = application_settings["image_directory"]
    camera_index = application_settings["camera_to_open"]
    default_scene_name = application_settings["default_scene_name"]
    target_scene_name = application_settings["target_scene_name"]

    valid_camera_indices = get_valid_camera_indices()
    print("Found cameras: ", valid_camera_indices)
    if camera_index not in valid_camera_indices:
        print("Chosen camera index ({}) not in list of valid cameras")
        return

    try:
        video_capture = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        # Record at 1080p
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

        # Always get the latest frame
        video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 0)

        image_files_to_search_for = [cv2.imread(join(image_directory, f)) for f in listdir(image_directory) if isfile(join(image_directory, f))]
    except Exception as e:
        print(e)
    
    obs = obsws(host, port)
    obs.connect()

    scenes = obs.call(requests.GetSceneList())
    print("Detected scenes in OBS: " + str(scenes))

    while True:
        print("Starting tick")
        try:
            start_time = time.clock()
            execute_tick(video_capture, image_files_to_search_for, obs, default_scene_name, target_scene_name)
            print("Tick took {} seconds".format(round(time.clock() - start_time, 2)), flush=True)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()