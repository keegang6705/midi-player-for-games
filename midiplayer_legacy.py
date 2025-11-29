import os
import time
import ctypes
import sys
import json
import win32gui
import win32con
import threading
from mido import MidiFile
from pynput.keyboard import Controller, Key, Listener
from colorama import Fore, Style, init
init(autoreset=True)


def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True

    ctypes.windll.shell32.ShellExecuteW(
        None, 
        "runas", 
        sys.executable, 
        " ".join(f'"{arg}"' for arg in sys.argv),
        None,
        1 
    )
    sys.exit()

def set_console_topmost():
    hwnd = win32gui.GetForegroundWindow()
    import win32console
    hwnd = win32console.GetConsoleWindow()
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,0, 0, 0, 0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        ctypes.windll.user32.MoveWindow(hwnd, 0, 0, 400, 600, True)
    else:
        print("Cannot find console window handle")

def parse_and_press_key(keyboard, key_string):
    """
    Parse key combinations like 'shift+z', 'ctrl+c', 'alt+x' and press them.
    Supports single keys and combinations with shift, ctrl, alt modifiers.
    """
    parts = key_string.lower().split('+')
    modifiers = []
    main_key = None
    
    for part in parts:
        if part == 'shift':
            modifiers.append(Key.shift)
        elif part == 'ctrl':
            modifiers.append(Key.ctrl)
        elif part == 'alt':
            modifiers.append(Key.alt)
        else:
            main_key = part.strip()
    
    if not main_key:
        print(f"Warning: Invalid key combination '{key_string}'")
        return
    
    # Press all modifiers
    for mod in modifiers:
        keyboard.press(mod)
    
    # Press the main key
    try:
        keyboard.press(main_key)
        keyboard.release(main_key)
    except Exception as e:
        print(f"Warning: Could not press key '{main_key}': {e}")
    
    # Release all modifiers
    for mod in reversed(modifiers):
        keyboard.release(mod)

set_console_topmost()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_keymaps():
    try:
        with open('keymap.json', 'r') as f:
            keymaps = json.load(f)
        return keymaps
    except FileNotFoundError:
        print("Error: keymap.json not found!")
        print("Please create a keymap.json file with your key mappings.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in keymap.json")
        sys.exit(1)

def load_settings():
    default_settings = {
        "selected_keymap": None,
        "range_mismatch_handling": 1,
        "speed_multiplier": 1.0,
        "target_duration": None,
        "midi_directories": ["D:/Files/Audio/mid"]
    }
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            return {**default_settings, **settings}
    except FileNotFoundError:
        return default_settings
    except json.JSONDecodeError:
        print("Warning: Invalid JSON format in settings.json, using defaults")
        return default_settings

def save_settings(settings):
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def select_keymap(keymaps, current_keymap=None):
    clear_console()
    print("\nAvailable mappings:")
    for i, name in enumerate(keymaps):
        current_marker = " (current)" if name == current_keymap else ""
        print(f"{i + 1}. {name}{current_marker}")
    print("X. Cancel")
    
    while True:
        choice = input("\nSelect mapping: ").upper()
        if choice == 'X':
            return None
        try:
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(keymaps):
                selected_map_name = list(keymaps.keys())[choice_num]
                return selected_map_name, {int(k): v for k, v in keymaps[selected_map_name].items()}
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(keymaps)}.")
        except ValueError:
            print("Invalid input. Please enter a number or 'X'.")

def format_duration(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def scan_midi_files_range(file_folder_tuples, note_to_key):
    """Scan MIDI files from multiple folders and return info with color coding."""
    results = []
    min_key = min(note_to_key.keys())
    max_key = max(note_to_key.keys())

    for f, folder in file_folder_tuples:
        try:
            midi_path = os.path.join(folder, f)
            midi = MidiFile(midi_path)
            duration = format_duration(midi.length)
            notes = []
            
            for track in midi.tracks:
                for msg in track:
                    if msg.type == 'note_on' and hasattr(msg, 'note'):
                        if 0 <= msg.note <= 127:
                            notes.append(msg.note)

            if not notes:
                colored_name = f"{Fore.LIGHTBLACK_EX}{f}{Style.RESET_ALL} ({duration})"
            elif min(notes) >= min_key and max(notes) <= max_key:
                colored_name = f"{Fore.GREEN}{f}{Style.RESET_ALL} ({duration})"
            else:
                colored_name = f"{Fore.YELLOW}{f}{Style.RESET_ALL} ({duration})"
        except Exception as e:
            colored_name = f"{Fore.RED}{f}{Style.RESET_ALL} (error)"

        results.append((f, folder, colored_name))
    return results

def list_midi_files(folders):
    """List all MIDI files from multiple folders."""
    if isinstance(folders, str):
        folders = [folders]
    
    midi_files = []
    for folder in folders:
        if os.path.isdir(folder):
            try:
                files = [f for f in os.listdir(folder) if f.lower().endswith((".mid", ".midi"))]
                midi_files.extend([(f, folder) for f in files])
            except Exception as e:
                print(f"Error reading directory {folder}: {e}")
    return midi_files

def get_nearest_key(note, note_to_key):
    return note_to_key[min(note_to_key.keys(), key=lambda x: abs(x - note))]

def check_midi_range(midi, note_to_key):
    min_key = min(note_to_key.keys())
    max_key = max(note_to_key.keys())

    notes_in_midi = []
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and hasattr(msg, 'note'):
                if 0 <= msg.note <= 127:
                    notes_in_midi.append(msg.note)
    
    if not notes_in_midi:
        return None 

    min_midi = min(notes_in_midi)
    max_midi = max(notes_in_midi)

    if min_midi >= min_key and max_midi <= max_key:
        return 1

    print(f"\nRange mismatch detected:")
    print(f"Keymap range: {min_key} - {max_key}")
    print(f"MIDI note range: {min_midi} - {max_midi}")

    print("\nOptions to handle this:")
    print("1. Scale all notes in the song to fit the range")
    print("2. Map notes to nearest available button")
    print("3. Discard notes that are out of range")

    while True:
        choice = input("Select option (1, 2, or 3): ")
        if choice in ('1', '2', '3'):
            return int(choice)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def scale_note(note, old_min, old_max, new_min, new_max):
    if old_max == old_min:
        return new_min
    scaled = (note - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
    return int(round(scaled))

def play_midi(file_path, note_to_key, selected_map_name, range_choice=1, 
              speed_multiplier=1.0, target_duration=None):
    try:
        midi = MidiFile(file_path)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return
    
    if range_choice is None:
        choice = check_midi_range(midi, note_to_key)
        if choice is None:
            print("No notes found in MIDI file.")
            return
    else:
        choice = range_choice

    if target_duration is not None:
        speed_multiplier = midi.length / target_duration
    
    min_key = min(note_to_key.keys())
    max_key = max(note_to_key.keys())
    
    old_notes = []
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and hasattr(msg, 'note'):
                if 0 <= msg.note <= 127:
                    old_notes.append(msg.note)
    
    old_min = min(old_notes) if old_notes else 0
    old_max = max(old_notes) if old_notes else 0

    keyboard = Controller()
    time_cursor = 0.0
    start_time = time.time()

    clear_console()
    print(f"\nPlaying '{file_path}'\nusing '{selected_map_name}' mapping")
    print(f"Speed: {speed_multiplier:.2f}x")
    print("in 3 seconds...")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)
    print("Press Ctrl+C to stop playback")

    try:
        for msg in midi:
            time_cursor += msg.time
            elapsed = time.time() - start_time
            sleep_time = time_cursor - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time / speed_multiplier)

            if msg.type == 'note_on' and msg.velocity > 0 and hasattr(msg, 'note'):
                note = msg.note
                
                if not (0 <= note <= 127):
                    continue
                
                if choice == 1:
                    scaled_note = scale_note(note, old_min, old_max, min_key, max_key)
                    key = note_to_key.get(scaled_note, get_nearest_key(scaled_note, note_to_key))
                elif choice == 2:
                    key = note_to_key.get(note, get_nearest_key(note, note_to_key))
                else:
                    if note < min_key or note > max_key:
                        continue
                    else:
                        key = note_to_key.get(note, get_nearest_key(note, note_to_key))

                parse_and_press_key(keyboard, key)

    except KeyboardInterrupt:
        print("\nPlayback stopped by user")
    except Exception as e:
        print(f"Error during playback: {e}")

def run_test_mapping(note_to_key, selected_map_name):
    test_notes = sorted(note_to_key.keys()) 
    keyboard = Controller()

    clear_console()
    print(f"\nRunning test for mapping '{selected_map_name}'...")
    print("Press Ctrl+C to stop test")
    time.sleep(2)

    try:
        for note in test_notes:
            key = note_to_key[note]
            print(f"Pressing note {note} mapped to key '{key}'")
            parse_and_press_key(keyboard, key)
            time.sleep(0.5)
        print("Test completed!")
    except KeyboardInterrupt:
        print("\nTest stopped by user")

def show_main_menu():
    clear_console()
    print("\nMain Menu:")
    print("1. Play Songs")
    print("2. Settings")
    print("3. Exit")
    while True:
        choice = input("\nSelect option: ").upper()
        if choice in ('1', '2', '3'):
            return int(choice)
        print("Invalid selection. Please enter 1-3.")

def show_settings_menu():
    clear_console()
    print("\nSettings:")
    print("1. Change Key Mapping")
    print("2. Default Range Mismatch Handling")
    print("3. Playback Speed")
    print("4. MIDI Directory")
    print("X. Return to Main Menu")
    while True:
        choice = input("\nSelect option: ").upper()
        if choice == 'X':
            return choice
        if choice in ('1', '2', '3', '4'):
            return int(choice)
        print("Invalid selection. Please enter 1-4 or 'X'.")

def set_range_mismatch_handling(current_setting):
    clear_console()
    print("\nDefault Range Mismatch Handling:")
    print(f"1. Scale all notes in the song to fit the range {'(current)' if current_setting == 1 else ''}")
    print(f"2. Map notes to nearest available button {'(current)' if current_setting == 2 else ''}")
    print(f"3. Discard notes that are out of range {'(current)' if current_setting == 3 else ''}")
    print("X. Cancel")
    
    while True:
        choice = input("\nSelect option: ").upper()
        if choice == 'X':
            return current_setting
        if choice in ('1', '2', '3'):
            return int(choice)
        print("Invalid choice. Please enter 1, 2, 3, or 'X'.")

def set_playback_speed(current_multiplier, current_duration):
    clear_console()
    print("\nPlayback Speed Settings:")
    print("1. Set Speed Multiplier")
    print("2. Set Target Duration")
    print("3. Reset to Default (1.0x)")
    print("X. Cancel")
    choice = input("\nSelect option: ").upper()
    
    if choice == "1":
        while True:
            speed_input = input("Enter speed multiplier (or X to cancel): ").upper()
            if speed_input == 'X':
                return current_multiplier, current_duration
            try:
                multiplier = float(speed_input)
                if multiplier > 0:
                    return multiplier, None
                print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number or 'X'.")
    
    elif choice == "2":
        while True:
            minutes_input = input("Enter target duration minutes (or X to cancel): ").upper()
            if minutes_input == 'X':
                return current_multiplier, current_duration
            try:
                minutes = int(minutes_input)
                seconds = int(input("Enter target duration seconds: "))
                if minutes >= 0 and 0 <= seconds < 60:
                    return None, (minutes * 60 + seconds)
                print("Invalid duration. Please enter valid minutes and seconds.")
            except ValueError:
                print("Invalid input. Please enter numbers.")
    
    elif choice == "3":
        return 1.0, None
    
    elif choice == "X":
        return current_multiplier, current_duration
    
    return current_multiplier, current_duration

def set_midi_directories(current_directories):
    """Manage list of MIDI directories."""
    while True:
        clear_console()
        print("\nManage MIDI Directories:")
        for i, dir_path in enumerate(current_directories, 1):
            print(f"{i}. {dir_path}")
        print("\nA. Add Directory")
        print("R. Remove Directory")
        print("X. Return to Settings")
        
        choice = input("\nSelect option: ").upper()
        
        if choice == 'X':
            return current_directories
        elif choice == 'A':
            print("Enter new directory path (or X to cancel):")
            new_path = input("> ").strip()
            if new_path.upper() == 'X':
                continue
            if new_path.startswith('"') and new_path.endswith('"'):
                new_path = new_path[1:-1]
            if os.path.isdir(new_path):
                if new_path not in current_directories:
                    current_directories.append(new_path)
                    print(f"Added: {new_path}")
                else:
                    print("This directory is already in the list.")
            else:
                print("Error: Directory does not exist.")
            input("Press Enter to continue...")
        elif choice == 'R':
            if not current_directories:
                print("No directories to remove.")
            else:
                print("\nSelect directory to remove:")
                for i, dir_path in enumerate(current_directories, 1):
                    print(f"{i}. {dir_path}")
                try:
                    remove_idx = int(input("Select number (or 0 to cancel): ")) - 1
                    if remove_idx == -1:
                        continue
                    if 0 <= remove_idx < len(current_directories):
                        removed = current_directories.pop(remove_idx)
                        print(f"Removed: {removed}")
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input.")
            input("Press Enter to continue...")

def main():
    run_as_admin()
    keymaps = load_keymaps()
    settings = load_settings()
    
    if settings["selected_keymap"] and settings["selected_keymap"] in keymaps:
        selected_map_name = settings["selected_keymap"]
        note_to_key = {int(k): v for k, v in keymaps[selected_map_name].items()}
    else:
        result = select_keymap(keymaps)
        if result is None:
            print("No keymap selected. Exiting.")
            return
        selected_map_name, note_to_key = result
        settings["selected_keymap"] = selected_map_name
        save_settings(settings)

    while True:
        choice = show_main_menu()
        
        if choice == 1:
            while True:
                clear_console()
                midi_files = list_midi_files(settings["midi_directories"])
                midi_info = scan_midi_files_range(midi_files, note_to_key)
                print("\nAvailable MIDI files and options:")
                print(f"{Fore.CYAN}0. Run test mapping keys{Style.RESET_ALL}")
                print(f"{Fore.CYAN}X. Return to Main Menu{Style.RESET_ALL}")
                for i, (_, _, colored_name) in enumerate(midi_info):
                    print(f"{i + 1}. {colored_name}")
                
                selection = input("\nSelect MIDI file or option: ").upper()
                if selection == 'X':
                    break
                try:
                    index = int(selection)
                    if index == 0:
                        run_test_mapping(note_to_key, selected_map_name)
                    elif 1 <= index <= len(midi_info):
                        filename, folder, _ = midi_info[index - 1]
                        file_path = os.path.join(folder, filename)
                        play_midi(file_path, note_to_key, selected_map_name, 
                                settings["range_mismatch_handling"], 
                                settings["speed_multiplier"], 
                                settings["target_duration"])
                except ValueError:
                    print("Invalid input. Please enter a number or 'X'.")
        
        elif choice == 2:
            while True:
                settings_choice = show_settings_menu()
                if settings_choice == 'X':
                    break
                elif settings_choice == 1:
                    result = select_keymap(keymaps, selected_map_name)
                    if result is not None:
                        selected_map_name, note_to_key = result
                        settings["selected_keymap"] = selected_map_name
                        save_settings(settings)
                        print(f"Key mapping changed to '{selected_map_name}'")
                elif settings_choice == 2:
                    settings["range_mismatch_handling"] = set_range_mismatch_handling(settings["range_mismatch_handling"])
                    save_settings(settings)
                elif settings_choice == 3:
                    settings["speed_multiplier"], settings["target_duration"] = set_playback_speed(
                        settings["speed_multiplier"], settings["target_duration"])
                    save_settings(settings)
                elif settings_choice == 4:
                    settings["midi_directories"] = set_midi_directories(settings["midi_directories"])
                    save_settings(settings)
        
        else:
            break

    print("\nThank you for using the MIDI player!")


if __name__ == "__main__":
    main()
