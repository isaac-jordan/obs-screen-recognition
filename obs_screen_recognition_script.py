from os import listdir
from os.path import isfile, join, dirname, realpath
import time
import json
from functools import partial
import logging
import click

from obswebsocket import obsws, requests
import numpy
import cv2
from mss import mss

logging.basicConfig(level=logging.ERROR)

host = "localhost"
port = 4444

VALID_RESOLUTIONS_ERROR_MESSAGE = "The only valid resolutions are currently 1080p, 1440p and 1200p. Your resolution is being detected as {resolution}."
VALID_RESOLUTIONS = [
    (1080, 1920),
    (1440, 2560),
    (1200, 1920)
]

print = partial(print, flush=True)

currently_in_default_scene = False
def execute_tick(screen_capture, monitor_to_capture, image_mask, image_descriptors, feature_detector, feature_matcher, num_good_matches_required, obs, default_scene_name, target_scene_name, show_debug_window):
    global currently_in_default_scene
    try:
        start_time = time.time()
        frame = numpy.array(screen_capture.grab(screen_capture.monitors[monitor_to_capture]))
        masked_frame = cv2.bitwise_and(frame, frame, mask=image_mask)
        
        image_is_in_frame, matches = frame_contains_one_or_more_matching_images(masked_frame, image_mask, image_descriptors, feature_detector, feature_matcher, num_good_matches_required, show_debug_window)

        tick_time = None
        if image_is_in_frame:
            if currently_in_default_scene:
                obs.call(requests.SetCurrentScene(target_scene_name))
                tick_time = round(time.time() - start_time, 2)

                currently_in_default_scene = False
        elif not currently_in_default_scene:
            assumed_render_delay_sec = 0.1
            # Compensates for the render delay, otherwise the scene changes too fast
            time.sleep(assumed_render_delay_sec)

            obs.call(requests.SetCurrentScene(default_scene_name))
            tick_time = round((time.time() - start_time) - assumed_render_delay_sec, 2)
            
            currently_in_default_scene = True
        return (tick_time, matches)
    except Exception as e:
        print(e)
    return (None, -1)

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

def get_good_matches(matches, num_good_matches_required, show_debug_window):
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])

            # Performance optimization when not in debug
            if len(good) >= num_good_matches_required and not show_debug_window:
                return good
    return good

def frame_contains_one_or_more_matching_images(frame, mask, image_descriptors, feature_detector, feature_matcher, num_good_matches_required, show_debug_window):
    if frame is not None:
        keypoints, keypoint_descriptors = feature_detector.detectAndCompute(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), mask)

        for image_descriptor in image_descriptors:
            matches = feature_matcher.knnMatch(keypoint_descriptors, image_descriptor, k=2)
            # Apply ratio test
            good = get_good_matches(matches, num_good_matches_required, show_debug_window)

            if show_debug_window:
                cv2.drawKeypoints(frame, keypoints, frame)
                cv2.imshow("obs-screen-recognition", cv2.resize(frame, (0, 0), fx=0.5, fy=0.5))
                cv2.waitKey(1)
                print("Num matches: {}".format(len(good)))
            
            if len(good) >= num_good_matches_required:
                return (True, len(good))
    return (False, len(good))

@click.command()
@click.option('--show-debug-window', is_flag=True)
@click.argument('resource-dir', type=click.Path(exists=True,file_okay=False, dir_okay=True))
@click.option('--password')
def main(resource_dir, password, show_debug_window):
    
    with open(dirname(realpath(__file__)) + "/settings.json") as settings_file:
        application_settings = json.load(settings_file)

    print("Running with settings:", application_settings)
    monitor_to_capture = application_settings["monitor_to_capture"]
    default_scene_name = application_settings["default_scene_name"]
    target_scene_name = application_settings["target_scene_name"]
    num_features_to_detect = application_settings["num_features_to_detect"]
    num_good_matches_required = application_settings["num_good_matches_required"]

    if password:
        obs = obsws(host, port, password)
    else:
        obs = obsws(host, port)
    obs.connect()

    scenes = obs.call(requests.GetSceneList())
    print("Detected scenes in OBS: " + str(scenes))

    if show_debug_window:
        cv2.startWindowThread()
        cv2.namedWindow("obs-screen-recognition")

    with mss() as screen_capture:
        initial_frame_resolution = numpy.array(screen_capture.grab(screen_capture.monitors[monitor_to_capture])).shape[0:2]
        screen_size = str(initial_frame_resolution[0]) + "p" # E.g. 1440p
        print("Detected monitor resolution to be {}".format(screen_size))
        if initial_frame_resolution not in VALID_RESOLUTIONS:
            print(VALID_RESOLUTIONS_ERROR_MESSAGE.format(resolution = initial_frame_resolution))
            exit(1)
    
        image_directory = resource_dir + "/" + screen_size
        mask_file = resource_dir + "/mask-" + screen_size + ".png"
        image_files_to_search_for = [cv2.cvtColor(cv2.imread(join(image_directory, f)), cv2.COLOR_BGR2GRAY) for f in listdir(image_directory) if isfile(join(image_directory, f))]
        image_mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)

        feature_detector = cv2.ORB_create(nfeatures=num_features_to_detect, scoreType=cv2.ORB_FAST_SCORE, nlevels=1, fastThreshold=10)
        feature_matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        image_descriptors = [feature_detector.detectAndCompute(image, None)[1] for image in image_files_to_search_for]

        while True:
            try:
                tick_time, num_matches = execute_tick(screen_capture, monitor_to_capture, image_mask, image_descriptors, feature_detector, feature_matcher, num_good_matches_required, obs, default_scene_name, target_scene_name, show_debug_window)
                if tick_time:
                    print("Tick took {} seconds. Suggested OBS source delay: {}ms. Num good matches: {}".format(tick_time, round(tick_time, 2) * 1000, num_matches))
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()