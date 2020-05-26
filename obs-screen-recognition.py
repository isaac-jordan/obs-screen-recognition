from os import listdir
from os.path import isfile, join

import obspython as obs
import cv2


# Docs: https://obsproject.com/docs/scripting.html

# User configurable settings
tick_interval_ms = 250
camera_index = None
image_path = None

# Global variables
video_capture = None
image_files = None

def script_load(settings):
    print("Script load!")


def script_unload():
    print("Script unload!")
    obs.timer_remove(execute_tick)
    try:
        video_capture.release()
    except Exception as e:
        print(e)


def script_defaults(settings):
    print("Script defaults load!")
    obs.obs_data_set_default_int(
        settings, "tick_interval_ms", tick_interval_ms)


def script_properties():
    global video_capture
    print("Script properties!")
    props = obs.obs_properties_create()
    obs.obs_properties_add_int(
        props, "tick_interval_ms", "Update Interval (milliseconds)", 250, 3600, 1)

    obs.obs_properties_add_path(props, "image_path", "Image Path", obs.OBS_PATH_DIRECTORY, "", None )

    p = obs.obs_properties_add_list(
        props, "camera_index", "Camera", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    if video_capture:
        video_capture.release()
    video_capture = None

    camera_indices = get_valid_camera_indices()
    print("Camera indices: " + str(camera_indices))
    for index in camera_indices:
        obs.obs_property_list_add_string(p, "Camera " + str(index), str(index))

    return props

def script_update(settings):
    global tick_interval_ms, camera_index, image_path, image_files, video_capture
    print("Script settings update!")

    tick_interval_ms = obs.obs_data_get_int(settings, "tick_interval_ms")
    new_camera_index = obs.obs_data_get_string(settings, "camera_index")
    new_image_path = obs.obs_data_get_string(settings, "image_path")
    print("Camera index", camera_index)
    print("Image path", image_path)

    if not new_image_path:
        image_path = None
    else:
        image_path = new_image_path

    if not new_camera_index:
        camera_index = None
    else:
        camera_index = [int(s) for s in new_camera_index.split() if s.isdigit()][0]

    if video_capture:
        video_capture.release()
    video_capture = None

    image_files = None

    # Start using the new interval
    obs.timer_remove(execute_tick)
    obs.timer_add(execute_tick, tick_interval_ms)



def execute_tick():
    global camera_index, video_capture, image_path, image_files
    if camera_index is not None and video_capture is None:
        print("Opening camera " + str(camera_index))
        try:
            video_capture = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        except Exception as e:
            print(e)
    
    if image_path is not None and not image_files is not None:
        print("HELLO?!")
        image_files_to_process = [cv2.imread(join(image_path, f), 0) for f in listdir(image_path) if isfile(join(image_path, f))]
        # print("Channels", [len(i.shape) for i in image_files_to_process])
        image_files = [cv2.resize(image, None, fx=0.5, fy=0.5) for image in image_files_to_process]
        print("Image files", image_files)

    if video_capture is not None:
        try:
            ret, frame = video_capture.read()

            if frame is not None:
                gray_scale_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2GRAY)
                cv2.imwrite(join(image_path, '..', 'recorded_frame_test.png'), gray_scale_frame)
                for image in image_files:
                    print(image.shape)
                    print(gray_scale_frame.shape)
                    result = cv2.matchTemplate(gray_scale_frame, image, cv2.TM_SQDIFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                    print(min_val, max_val)
                    if min_val < 0.1:
                        print("LOOKS LIKE MAP IS OPEN!")
                    else:
                        print("MAP NOT OPEN")
                    # print(min_loc, max_loc)
        except Exception as e:
            print(e)
    


indices_cache = None
def get_valid_camera_indices():
    global indices_cache
    # checks the first 10 indexes.
    if indices_cache:
        return indices_cache
    index = 0
    arr = []
    max_to_check = 10
    while index <= max_to_check:
        cap = cv2.VideoCapture(index)
        ret, frame = cap.read()
        if ret:
            print("Got a read from index " + str(index))
            arr.append(index)
            cap.release()
        index += 1
    indices_cache = arr
    return indices_cache