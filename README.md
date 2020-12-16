# obs-screen-recognition

This script is designed to recognise specific content on your screen and change scenes within OBS based on that content.

### PLEASE NOTE: THIS SCRIPT IS NOT INTENDED TO BE RUN FROM INSIDE OBS AS AN "OBS SCRIPT". PLEASE FOLLOW THE USAGE INSTRUCTIONS CAREFULLY.

### ALSO NOTE: THIS ONLY WORKS WITH OFFICIAL OBS - NOT STREAMLABS OBS

## Hell Let Loose Map Detection

The initial use-case is to recognise when the map is open in Hell Let Loose, and change scenes in OBS so that map is not revealed to the live broadcast viewers.

The `hll` folder contains images which are always displayed when the HLL map is open, and a mask file to reduce the image down to where those images show. These images are organized for screen resolutions (currently only 1080p and 1440p). Use the "--show-debug-window" option to see what the script sees after applying the mask.

## Usage
1. Clone/download repository and extract into any folder (e.g. Downloads)
2. Install Python 3.8. **Click "Add Python 3.8 to PATH at the bottom".**
3. Install a terminal app if you don't already have one e.g. [Git Bash](https://gitforwindows.org/)
4. Open up your terminal
5. Navigate to where you extracted this repository (e.g. `cd Downloads/obs-screen-recognition`)
4. Install the dependencies using pip in your terminal: `python -m pip install -r requirements.txt`
5. Install the [obs-websocket plugin](https://obsproject.com/forum/resources/obs-websocket-remote-control-obs-studio-from-websockets.466/) for OBS (Windows Installer works fine)
6. Start (or restart) OBS (Note that Streamlabs OBS will not work)
6. Configure the settings in `settings.json`:
    - **monitor_to_capture**: If you have multiple monitors this specifies which one should be used.
    - **default_scene_name**: OBS scene to open when the script doesn't match an image (e.g. when the map isn't open in HLL)
    - **target_scene_name**: OBS scene to open when the script recognizes an image_directory image in the monitor contents (e.g. when you want the map hidden in HLL)
    - num_features_to_detect: Affects the accuracy and speed of the matching.
    - num_good_matches_required: Affects the false-match frequency
7. Run the script: `obs_screen_recognition_script.py`, providing the folder where matching images are stored (currently only HLL game supported, so `$> python obs_screen_recognition_script.py ./hll`) tweak settings/images if necessary (to display what the script is seeing, use the `show-debug-window` flag as in `$> python obs_screen_recognition_script.py --show-debug-window ./hll`).
8. Since the script is not instantaneous (it takes a small amount of time to recognise the images, and a small amount of time to contact OBS), it is probably a good idea to look at the script's _"Suggested OBS source delay"_ logs and set your game source delay (in OBS, right click on the source, select _Filters_ and add a _Render Delay_) to something around that. ~150ms seems to work well on the creator's hardware.
