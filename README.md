# obs-screen-recognition

This script is designed to recognise specific content on your screen and change scenes within OBS based on that content.

### PLEASE NOTE: THIS SCRIPT IS NOT INTENDED TO BE RUN FROM INSIDE OBS AS AN "OBS SCRIPT". PLEASE FOLLOW THE USAGE INSTRUCTIONS CAREFULLY.

### ALSO NOTE: THIS ONLY WORKS WITH OFFICIAL OBS - NOT STREAMLABS OBS

## Hell Let Loose Map Detection

The initial use-case is to recognise when the map is open in Hell Let Loose, and change scenes in OBS so that map is not revealed to the live broadcast viewers.

The hll_map_open_detection folder contains images which are always displayed when the HLL map is open, and a mask file to reduce the image down to where those images show. These images are designed for a 1440p monitor, and may need to be recreated for a different monitor size (especially the mask file). Use the "show_debug_window" setting to see what the script sees after applying the mask.

## Usage
1. Clone/download repository and extract into any folder (e.g. Downloads)
2. Install Python 3.6. **Click "Add Python 3.6 to PATH at the bottom".**
3. Install a terminal app if you don't already have one e.g. [Git Bash](https://gitforwindows.org/)
4. Open up your terminal
5. Navigate to where you extracted this repository (e.g. `cd Downloads/obs-screen-recognition`)
4. Install the dependencies using pip in your terminal: `pip install -r requirements.txt`
5. Install the [obs-websocket plugin](https://obsproject.com/forum/resources/obs-websocket-remote-control-obs-studio-from-websockets.466/) for OBS (Windows Installer works fine)
6. Start (or restart) OBS (Note that Streamlabs OBS will not work)
6. Configure the settings in `settings.json`:
    - **monitor_to_capture**: If you have multiple monitors this specifies which one should be used.
    - **screen_format**: Your screen format, either `1080p` (if you play in Full HD) or `1440p` (if you play in QUad HD). _Additional formats might be added with your help._
    - **default_scene_name**: OBS scene to open when the script doesn't match an image (e.g. when the map isn't open in HLL)
    - **target_scene_name**: OBS scene to open when the script recognizes an image_directory image in the monitor contents (e.g. when you want the map hidden in HLL)
    - num_features_to_detect: Affects the accuracy and speed of the matching.
    - num_good_matches_required: Affects the false-match frequency
    - show_debug_window: Set to true in order to view the screen that the script is trying to match image_directory images in
7. Run the script: `obs_screen_recognition_script.py`, providing the folder where matching images are stored (currently only one game supported, `hll`) tweak settings/images if necessary (Enable the `--show_debug_window` flag to display what the script is seeing).
8. Since the script is not instantaneous (it takes a small amount of time to recognise the images, and a small amount of time to contact OBS), it is probably a good idea to look at the script's "Suggested OBS source delay" logs and set your scene delay (in OBS) to something around that. ~150ms seems to work well on the creator's hardware.
