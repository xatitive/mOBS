import obspython as S
import simpleaudio as sa
import psutil
from pathlib import Path
from notifypy import Notify

enabled = True
debug_mode = False
play_start_sound = True
play_clip_sound = True
auto_start_buffer = True
clip_sound_path = ""
start_sound_path = ""


notification = Notify(
  default_notification_application_name="Open Broadcaster Software",
  default_notification_title="mOBS",
  default_notification_message="mOBS started",
  default_notification_audio=None,
  block=False
)

class Hotkey:
    def __init__(self, callback, obs_settings, _id):
        self.obs_data = obs_settings
        self.hotkey_id = S.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self.callback = callback
        self._id = _id

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def register_hotkey(self):
        description = str(self._id)
        self.hotkey_id = S.obs_hotkey_register_frontend(
            "htk_id" + str(self._id), description, self.callback
        )
        S.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)

    def load_hotkey(self):
        self.hotkey_saved_key = S.obs_data_get_array(
            self.obs_data, "htk_id" + str(self._id)
        )
        S.obs_data_array_release(self.hotkey_saved_key)

    def save_hotkey(self):
        self.hotkey_saved_key = S.obs_hotkey_save(self.hotkey_id)
        S.obs_data_set_array(
            self.obs_data, "htk_id" + str(self._id), self.hotkey_saved_key
        )
        S.obs_data_array_release(self.hotkey_saved_key)


class h:
    htk_copy = None

h1 = h()

class Data:
    _text_ = None
    _int_ = None
    _settings_ = None

def save(prop, props):
    if not Data._settings_:
        return
    p = Path(__file__).absolute()  # current script path
    file = p.parent / "saved_settings.json"
    try:
        content = S.obs_data_get_json(Data._settings_)
        with open(file, "w") as f:
            f.write(content)
    except Exception as e:
        print(e, "cannot write to file")

def script_save_json_settings():
    p = Path(__file__).absolute()  # current script path
    file = p.parent / "saved_settings.json"
    try:
        content = S.obs_data_get_json(Data._settings_)
        with open(file, "w") as f:
            f.write(content)
    except Exception as e:
        print(e, "cannot write to file")


def script_description():
    return "Adds some custom QoL clipping features currently not currently avaliable"

def script_load(settings):
    global debug_mode
    global h1
    if debug_mode: 
        print("[mOBS] Loaded")

    notification.message = "mOBS started"
    notification.send()
    h1.htk_copy = Hotkey((clip_sound), settings, "mOBS Hotkey")
    script_update(settings)
    script_save_json_settings()
    if play_start_sound != False:
        start_sound()
    if auto_start_buffer != False:
        S.obs_frontend_replay_buffer_start()


def script_unload():
    if debug_mode: 
        print("[mOBS] Unloaded")
    notification.message = "mOBS stopped"
    notification.send()

def script_defaults(settings):
    
    global global_settings
    global debug_mode
    if debug_mode: 
        print("[mOBS] >Loading defaults")

    S.obs_data_set_default_bool(settings, "enabled", enabled)
    S.obs_data_set_default_bool(settings, "debug_mode", debug_mode)
    S.obs_data_set_default_bool(settings, "auto_start_buffer", enabled)
    S.obs_data_set_default_bool(settings, "play_start_sound", enabled)
    S.obs_data_set_default_bool(settings, "play_clip_sound", enabled)

def script_properties():
    if debug_mode: 
        print("[mOBS] Setting properties")

    props = S.obs_properties_create()

    S.obs_properties_add_bool(props, "enabled", "Enabled")
    S.obs_properties_add_bool(props, "debug_mode", "Debug mode")
    S.obs_properties_add_bool(props, "auto_start_buffer", "Replay buffer start on load")
    S.obs_properties_add_bool(props, "play_start_sound", "Play sound on start")
    S.obs_properties_add_bool(props, "play_clip_sound", "Play sound on clip")
    S.obs_properties_add_path(props, "clip_sound_path", "Path to clip sound", S.OBS_PATH_FILE, "", None)
    S.obs_properties_add_path(props, "start_sound_path", "Path to start sound", S.OBS_PATH_FILE, "", None)
    S.obs_properties_add_button(props, "save", "Save", save)

    return props

def script_save(settings):
    if debug_mode: 
        print("[mOBS] Saving settings")
    h1.htk_copy.save_hotkey()
    script_update(settings)

def clip_sound(pressed):
        sa.WaveObject.from_wave_file(clip_sound_path).play()

def start_sound():
    sa.WaveObject.from_wave_file(start_sound_path).play()

def script_update(settings):
    global enabled
    global debug_mode
    global auto_start_buffer
    global play_start_sound
    global play_clip_sound
    global clip_sound_path
    global start_sound_path
    if debug_mode: 
        print("[mOBS] Updating settings")

    enabled = S.obs_data_get_bool(settings, "enabled")
    debug_mode = S.obs_data_get_bool(settings, "debug_mode")
    auto_start_buffer = S.obs_data_get_bool(settings, "auto_start_buffer")
    play_start_sound = S.obs_data_get_bool(settings, "play_start_sound")
    play_clip_sound = S.obs_data_get_bool(settings, "play_clip_sound")
    clip_sound_path = S.obs_data_get_string(settings, "clip_sound_path")
    start_sound_path = S.obs_data_get_string(settings, "start_sound_path")
    Data._settings_ = settings
    notification.message = "mOBS settings updated"
    notification.send()
