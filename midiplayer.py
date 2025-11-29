import os,sys
import sys
import time
import json
from mido import MidiFile
from pynput.keyboard import Controller, Key, Listener


class MidiPlayer:
    def __init__(self, keymap_file='keymap.json', settings_file='settings.json'):
        self.keymap_file = keymap_file
        self.settings_file = settings_file
        self.keymaps = {}
        self.settings = {}
        self.stop_playback = False
        self.listener = None
        self.keyboard = Controller()
        self._load_files()

    def resource_path(self,relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    
    def _load_files(self):
        self.keymaps = self._load_keymaps()
        self.settings = self._load_settings()
    
    def _load_keymaps(self):
        try:
            with open(self.resource_path(self.keymap_file), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {self.keymap_file} not found!")
        except json.JSONDecodeError:
            raise ValueError(f"Error: Invalid JSON format in {self.keymap_file}")
    
    def _load_settings(self):
        default_settings = {
            "selected_keymap": None,
            "range_mismatch_handling": 1,
            "speed_multiplier": 1.0,
            "target_duration": 360,
            "midi_directories": [os.path.expanduser("~/Music")]
        }
        try:
            with open(self.settings_file, 'r') as f:
                loaded = json.load(f)
                settings = {**default_settings, **loaded}
                if 'midi_directory' in settings and 'midi_directories' not in settings:
                    settings['midi_directories'] = [settings.pop('midi_directory')]
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            return default_settings
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_keymaps_list(self):
        return list(self.keymaps.keys())
    
    def set_keymap(self, keymap_name):
        if keymap_name not in self.keymaps:
            return False
        self.settings["selected_keymap"] = keymap_name
        self.save_settings()
        return True
    
    def get_current_keymap(self):
        keymap_name = self.settings.get("selected_keymap")
        if keymap_name and keymap_name in self.keymaps:
            return {int(k): v for k, v in self.keymaps[keymap_name].items()}
        return None
    
    def get_keymap_name(self):
        return self.settings.get("selected_keymap")
    
    def add_midi_directory(self, directory):
        if not os.path.isdir(directory):
            return False
        if directory not in self.settings["midi_directories"]:
            self.settings["midi_directories"].append(directory)
            self.save_settings()
        return True
    
    def remove_midi_directory(self, directory):
        if directory in self.settings["midi_directories"]:
            self.settings["midi_directories"].remove(directory)
            self.save_settings()
            return True
        return False
    
    def get_midi_directories(self):
        return self.settings.get("midi_directories", [os.path.expanduser("~/Music")])
    
    def get_midi_directory(self):
        dirs = self.get_midi_directories()
        return dirs[0] if dirs else os.path.expanduser("~/Music")
    
    def set_playback_speed(self, speed_multiplier=None, target_duration=None):
        if speed_multiplier is not None and speed_multiplier > 0:
            self.settings["speed_multiplier"] = speed_multiplier
            self.settings["target_duration"] = None
        elif target_duration is not None and target_duration > 0:
            self.settings["target_duration"] = target_duration
            self.settings["speed_multiplier"] = 1.0
        self.save_settings()
    
    def get_playback_speed(self):
        return {
            "speed_multiplier": self.settings.get("speed_multiplier", 1.0),
            "target_duration": self.settings.get("target_duration")
        }
    
    def set_range_mismatch_handling(self, mode):
        if mode in (1, 2, 3):
            self.settings["range_mismatch_handling"] = mode
            self.save_settings()
            return True
        return False
    
    def get_range_mismatch_handling(self):
        return self.settings.get("range_mismatch_handling", 1)
    
    def list_midi_files(self):
        files = []
        for directory in self.get_midi_directories():
            if not os.path.isdir(directory):
                continue
            for f in os.listdir(directory):
                if f.lower().endswith((".mid", ".midi")) and f not in files:
                    files.append(f)
        return sorted(files)
    
    def parse_and_press_key(self, key_string):
        parts = key_string.lower().split('+')
        modifiers = []
        main_key = None
        for part in parts:
            part = part.strip()
            if part == 'shift':
                modifiers.append(Key.shift)
            elif part == 'ctrl':
                modifiers.append(Key.ctrl)
            elif part == 'alt':
                modifiers.append(Key.alt)
            else:
                main_key = part
        if not main_key:
            return False
        for mod in modifiers:
            self.keyboard.press(mod)
        try:
            self.keyboard.press(main_key)
            self.keyboard.release(main_key)
        except Exception:
            for mod in reversed(modifiers):
                self.keyboard.release(mod)
            return False
        for mod in reversed(modifiers):
            self.keyboard.release(mod)
        return True
    
    def _on_key_press(self, key):
        if key == Key.esc:
            self.stop_playback = True
    
    def _start_key_listener(self):
        self.stop_playback = False
        self.listener = Listener(on_press=self._on_key_press)
        self.listener.start()
    
    def _stop_key_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def get_midi_info(self, filename):
        try:
            for directory in self.get_midi_directories():
                filepath = os.path.join(directory, filename)
                if os.path.exists(filepath):
                    midi = MidiFile(filepath)
                    notes = []
                    for track in midi.tracks:
                        for msg in track:
                            if msg.type == 'note_on' and hasattr(msg, 'note') and 0 <= msg.note <= 127:
                                notes.append(msg.note)
                    return {
                        'filename': filename,
                        'duration': midi.length,
                        'note_range': (min(notes), max(notes)) if notes else None,
                        'has_notes': len(notes) > 0
                    }
            return {'filename': filename, 'error': 'File not found'}
        except Exception as e:
            return {'filename': filename, 'error': str(e)}
    
    def get_keymap_range(self):
        keymap = self.get_current_keymap()
        if not keymap:
            return None
        return (min(keymap.keys()), max(keymap.keys()))
    
    def check_midi_range(self, filename):
        keymap = self.get_current_keymap()
        if not keymap:
            return None
        info = self.get_midi_info(filename)
        if 'error' in info or not info.get('has_notes'):
            return 'no_notes'
        min_key, max_key = self.get_keymap_range()
        min_note, max_note = info['note_range']
        if min_note >= min_key and max_note <= max_key:
            return 'compatible'
        return {'status': 'mismatch', 'keymap_range': (min_key, max_key), 'midi_range': (min_note, max_note)}
    
    @staticmethod
    def scale_note(note, old_min, old_max, new_min, new_max):
        if old_max == old_min:
            return new_min
        scaled = (note - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
        return int(round(scaled))
    
    @staticmethod
    def get_nearest_key(note, note_to_key):
        return note_to_key[min(note_to_key.keys(), key=lambda x: abs(x - note))]
    
    def play_midi(self, filename, on_progress=None, on_status=None):
        self.stop_playback = False  # Reset stop flag before starting playback
        keymap = self.get_current_keymap()
        if not keymap:
            if on_status:
                on_status("No keymap selected")
            return False
        filepath = None
        for directory in self.get_midi_directories():
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                filepath = path
                break
        if not filepath:
            if on_status:
                on_status("MIDI file not found")
            return False
        try:
            midi = MidiFile(filepath)
        except Exception as e:
            if on_status:
                on_status(f"Error loading MIDI: {e}")
            return False
        range_check = self.check_midi_range(filename)
        if range_check == 'no_notes':
            if on_status:
                on_status("No notes found")
            return False
        range_mode = self.get_range_mismatch_handling()
        speed_multiplier = self.settings.get("speed_multiplier", 1.0)
        target_duration = self.settings.get("target_duration")
        if target_duration is not None and target_duration > 0:
            speed_multiplier = midi.length / target_duration
        old_notes = []
        for track in midi.tracks:
            for msg in track:
                if msg.type == 'note_on' and hasattr(msg, 'note') and 0 <= msg.note <= 127:
                    old_notes.append(msg.note)
        old_min = min(old_notes) if old_notes else 0
        old_max = max(old_notes) if old_notes else 0
        min_key, max_key = self.get_keymap_range()
        self._start_key_listener()
        time_cursor = 0.0
        start_time = time.time()
        if on_status:
            on_status(f"Playing {filename}")
        try:
            for msg_index, msg in enumerate(midi):
                if self.stop_playback:
                    if on_status:
                        on_status("Stopped")
                    return False
                time_cursor += msg.time
                elapsed = time.time() - start_time
                sleep_time = time_cursor - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time / speed_multiplier)
                if msg.type == 'note_on' and msg.velocity > 0 and hasattr(msg, 'note'):
                    note = msg.note
                    if not (0 <= note <= 127):
                        continue
                    if range_mode == 1:
                        scaled_note = self.scale_note(note, old_min, old_max, min_key, max_key)
                        key = keymap.get(scaled_note, self.get_nearest_key(scaled_note, keymap))
                    elif range_mode == 2:
                        key = keymap.get(note, self.get_nearest_key(note, keymap))
                    else:
                        if note < min_key or note > max_key:
                            continue
                        key = keymap.get(note, self.get_nearest_key(note, keymap))
                    self.parse_and_press_key(key)
                if on_progress:
                    on_progress(msg_index)
            if on_status:
                on_status("Completed")
            return True
        except Exception as e:
            if on_status:
                on_status(f"Error: {e}")
            return False
        finally:
            self._stop_key_listener()
    
    def test_keymap(self, on_progress=None, on_status=None):
        self.stop_playback = False  # Reset stop flag before starting test
        keymap = self.get_current_keymap()
        if not keymap:
            if on_status:
                on_status("No keymap")
            return False
        test_notes = sorted(keymap.keys())
        self._start_key_listener()
        if on_status:
            on_status(f"Testing {self.get_keymap_name()}")
        try:
            for index, note in enumerate(test_notes):
                if self.stop_playback:
                    if on_status:
                        on_status("Stopped")
                    return False
                key = keymap[note]
                if on_status:
                    on_status(f"Note {note} -> {key}")
                self.parse_and_press_key(key)
                time.sleep(0.25)
                if on_progress:
                    on_progress(index, len(test_notes))
            if on_status:
                on_status("Completed")
            return True
        except Exception as e:
            if on_status:
                on_status(f"Error: {e}")
            return False
        finally:
            self._stop_key_listener()


if __name__ == "__main__":
    player = MidiPlayer()
    print("Keymaps:", player.get_keymaps_list())
    print("Current:", player.get_keymap_name())
    print("Directories:", player.get_midi_directories())
