import os
import sys
import time
import json
import ctypes
from mido import MidiFile

SCANCODE_MAP = {
    'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12, 'f': 0x21,
    'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'm': 0x32, 'n': 0x31, 'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13,
    's': 0x1F, 't': 0x14, 'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D,
    'y': 0x15, 'z': 0x2C,
    '0': 0x0B, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A,
    'space': 0x39, 'enter': 0x1C, 'tab': 0x0F, 'backspace': 0x0E,
    'escape': 0x01, 'delete': 0xE053, 'insert': 0xE052,
    'up': 0xE048, 'down': 0xE050, 'left': 0xE04B, 'right': 0xE04D,
    'home': 0xE047, 'end': 0xE04F, 'pageup': 0xE049, 'pagedown': 0xE051,
    'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E, 'f5': 0x3F,
    'f6': 0x40, 'f7': 0x41, 'f8': 0x42, 'f9': 0x43, 'f10': 0x44,
    'f11': 0x57, 'f12': 0x58,
}

MODIFIER_SCANCODES = {
    'shift': 0x2A,
    'ctrl': 0x1D,
    'alt': 0x38
}

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001

class MidiPlayer:
    def __init__(self, keymap_file='keymap.json', settings_file='settings.json'):
        self.keymap_file = keymap_file
        self.settings_file = settings_file
        self.keymaps = {}
        self.settings = {}
        self.stop_playback = False
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
            "range_mismatch_handling": 3,
            "speed_multiplier": 1.0,
            "target_duration": 360,
            "playback_mode": 0,
            "midi_directories": [os.path.expanduser("~/Music")],
            "selected_language": "en",
            "window_topmost": True,
            "countdown_duration": 3
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
        if mode in (1, 2, 3, 4, 5, 6):
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
            if part in MODIFIER_SCANCODES:
                modifiers.append(part)
            else:
                main_key = part
        
        if not main_key or main_key not in SCANCODE_MAP:
            return False
        
        scancode = SCANCODE_MAP[main_key]
        is_extended = scancode > 0xFF
        
        for mod in modifiers:
            mod_scancode = MODIFIER_SCANCODES[mod]
            ctypes.windll.user32.keybd_event(0, mod_scancode, KEYEVENTF_SCANCODE, 0)
        
        flags = KEYEVENTF_SCANCODE
        if is_extended:
            flags |= KEYEVENTF_EXTENDEDKEY
            scancode = scancode & 0xFF
        
        ctypes.windll.user32.keybd_event(0, scancode, flags, 0)
        time.sleep(0.01)
        ctypes.windll.user32.keybd_event(0, scancode, flags | KEYEVENTF_KEYUP, 0)
        
        for mod in reversed(modifiers):
            mod_scancode = MODIFIER_SCANCODES[mod]
            ctypes.windll.user32.keybd_event(0, mod_scancode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
        
        return True
    
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
    
    @staticmethod
    def _find_optimal_range(notes, min_key, max_key):
        """Find the range in MIDI notes that maps to the most keymap keys."""
        if not notes:
            return 0, 127
        
        unique_notes = sorted(set(notes))
        best_range = (unique_notes[0], unique_notes[-1])
        best_count = 0
        
        for i, start_note in enumerate(unique_notes):
            for end_note in unique_notes[i:]:
                count = len([n for n in unique_notes if start_note <= n <= end_note])
                if count > best_count:
                    best_count = count
                    best_range = (start_note, end_note)
        
        return best_range
    
    def play_midi(self, filename, on_progress=None, on_status=None):
        self.stop_playback = False
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
        
        # Mode 6: Find optimal range to get most keys
        if range_mode == 6:
            old_min, old_max = self._find_optimal_range(old_notes, min_key, max_key)
        
        countdown = self.settings.get("countdown_duration", 3)
        if countdown > 0:
            for i in range(countdown, 0, -1):
                if self.stop_playback:
                    return False
                if on_status:
                    on_status(f"Starting in {i}...")
                time.sleep(1)
        
        time_cursor = 0.0
        start_time = time.time()
        total_msgs = sum(1 for _ in midi)
        midi = MidiFile(filepath)
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
                    elif range_mode == 3:
                        if note < min_key or note > max_key:
                            continue
                        key = keymap.get(note, self.get_nearest_key(note, keymap))
                    elif range_mode == 4:
                        offset = min_key - old_min
                        mapped_note = note + offset
                        if mapped_note > max_key:
                            continue
                        key = keymap.get(mapped_note, self.get_nearest_key(mapped_note, keymap))
                    elif range_mode == 5:
                        offset = max_key - old_max
                        mapped_note = note + offset
                        if mapped_note < min_key:
                            continue
                        key = keymap.get(mapped_note, self.get_nearest_key(mapped_note, keymap))
                    elif range_mode == 6:
                        scaled_note = self.scale_note(note, old_min, old_max, min_key, max_key)
                        key = keymap.get(scaled_note, self.get_nearest_key(scaled_note, keymap))
                    self.parse_and_press_key(key)
                if on_progress and total_msgs > 0:
                    progress = int((msg_index / total_msgs) * 100)
                    on_progress(progress)
            if on_status:
                on_status("Completed")
            return True
        except Exception as e:
            if on_status:
                on_status(f"Error: {e}")
            return False
    
    def test_keymap(self, on_progress=None, on_status=None):
        self.stop_playback = False
        keymap = self.get_current_keymap()
        if not keymap:
            if on_status:
                on_status("No keymap")
            return False
        test_notes = sorted(keymap.keys())
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
                    progress = int(((index + 1) / len(test_notes)) * 100)
                    on_progress(progress, 100)
            if on_status:
                on_status("Completed")
            return True
        except Exception as e:
            if on_status:
                on_status(f"Error: {e}")
            return False


if __name__ == "__main__":
    player = MidiPlayer()
    print("Keymaps:", player.get_keymaps_list())
    print("Current:", player.get_keymap_name())
    print("Directories:", player.get_midi_directories())