import os
import time
import ctypes
import sys
import json
import win32gui
import win32con
from mido import MidiFile
from pynput.keyboard import Controller
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

set_console_topmost()
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

def select_keymap(keymaps):
    print("\nAvailable mappings:")
    for i, name in enumerate(keymaps):
        print(f"{i + 1}. {name}")
    
    while True:
        try:
            choice = int(input("\nSelect mapping: ")) - 1
            if 0 <= choice < len(keymaps):
                selected_map_name = list(keymaps.keys())[choice]
                return selected_map_name, {int(k): v for k, v in keymaps[selected_map_name].items()}
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(keymaps)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def format_duration(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def scan_midi_files_range(files, folder, note_to_key):
    results = []
    min_key = min(note_to_key.keys())
    max_key = max(note_to_key.keys())

    for f in files:
        try:
            midi_path = os.path.join(folder, f)
            midi = MidiFile(midi_path)
            duration = format_duration(midi.length)  # แปลงเป็น mm:ss
            notes = [msg.note for msg in midi if msg.type == 'note_on']

            if not notes:
                colored_name = f"{Fore.LIGHTBLACK_EX}{f}{Style.RESET_ALL} ({duration})"
            elif min(notes) >= min_key and max(notes) <= max_key:
                colored_name = f"{Fore.GREEN}{f}{Style.RESET_ALL} ({duration})"
            else:
                colored_name = f"{Fore.YELLOW}{f}{Style.RESET_ALL} ({duration})"
        except Exception:
            colored_name = f"{Fore.RED}{f}{Style.RESET_ALL} (error)"

        results.append((f, colored_name))
    return results



def list_midi_files(folder="."):
    return [f for f in os.listdir(folder) if f.lower().endswith((".mid", ".midi"))]

def select_midi_or_test(midi_info):
    print("\nAvailable MIDI files and test option:")
    print(f"{Fore.CYAN}0. Run test mapping keys{Style.RESET_ALL}")
    for i, (_, colored_name) in enumerate(midi_info):
        print(f"{i + 1}. {colored_name}")
    
    while True:
        try:
            index_input = int(input("\nSelect MIDI file or test option: "))
            if index_input == 0:
                return None
            elif 1 <= index_input <= len(midi_info):
                return midi_info[index_input - 1][0]
            else:
                print(f"Invalid selection. Please enter a number between 0 and {len(midi_info)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_nearest_key(note, note_to_key):
    return note_to_key[min(note_to_key.keys(), key=lambda x: abs(x - note))]

def check_midi_range(midi, note_to_key):
    min_key = min(note_to_key.keys())
    max_key = max(note_to_key.keys())

    notes_in_midi = [msg.note for msg in midi if msg.type == 'note_on']
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

def play_midi(file_path, note_to_key, selected_map_name):
    try:
        midi = MidiFile(file_path)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return
    
    choice = check_midi_range(midi, note_to_key)
    if choice is None:
        print("No notes found in MIDI file.")
        return

    min_key = min(note_to_key.keys())
    max_key = max(note_to_key.keys())
    old_notes = [msg.note for msg in midi if msg.type == 'note_on']
    old_min = min(old_notes) if old_notes else 0
    old_max = max(old_notes) if old_notes else 0

    keyboard = Controller()
    time_cursor = 0.0
    start_time = time.time()

    print(f"\nPlaying '{file_path}'\nusing '{selected_map_name}' mapping\nin 3 seconds...")
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
                time.sleep(sleep_time)

            if msg.type == 'note_on' and msg.velocity > 0:
                note = msg.note
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

                keyboard.press(key)
                keyboard.release(key)

    except KeyboardInterrupt:
        print("\nPlayback stopped by user")
    except Exception as e:
        print(f"Error during playback: {e}")


def run_test_mapping(note_to_key, selected_map_name):
    test_notes = sorted(note_to_key.keys()) 
    keyboard = Controller()

    print(f"\nRunning test for mapping '{selected_map_name}'...")
    print("Press Ctrl+C to stop test")
    time.sleep(2)

    try:
        for note in test_notes:
            key = note_to_key[note]
            print(f"Pressing note {note} mapped to key '{key}'")
            keyboard.press(key)
            keyboard.release(key)
            time.sleep(0.5)
        print("Test completed!")
    except KeyboardInterrupt:
        print("\nTest stopped by user")

def main():
    run_as_admin()
    keymaps = load_keymaps()
    selected_map_name, note_to_key = select_keymap(keymaps)
    
    midi_folder = "D:/Files/Audio/mid"

    while True:
        midi_files = list_midi_files(midi_folder)
        midi_info = scan_midi_files_range(midi_files, midi_folder, note_to_key)
        selection = select_midi_or_test(midi_info)
        if selection is None:
            run_test_mapping(note_to_key, selected_map_name)
        else:
            file_path = os.path.join(midi_folder, selection)
            play_midi(file_path, note_to_key, selected_map_name)

    input("\nPress Enter to exit...")



if __name__ == "__main__":
    main()