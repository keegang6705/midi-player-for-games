# MIDI Player for Games

A powerful MIDI player designed specifically for playing custom game soundtracks with flexible key mapping and smooth playback control.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-2.1-blue)

## Features

- 🎵 **Multiple Keymap Profiles** - Create and switch between different key mappings for different games
- ⚙️ **Flexible Playback Control** - Adjust playback speed or set target duration
- 📍 **6 Range Handling Modes** - Scale, nearest key, discard, align-low, align-high, or optimal range
- 🎹 **Key Combinations** - Support for modifier keys (Shift, Ctrl, Alt) in key mappings
- 🖥️ **Modern PyQt5 GUI** - Clean, intuitive interface with real-time file info
- 📁 **Multiple MIDI Directories** - Organize MIDI files across multiple folders
- ⌨️ **Keymap Testing** - Test your key mappings with visual feedback
- ⏱️ **Countdown Timer** - Configurable startup countdown (0-10 seconds)
- 🌍 **Multi-Language** - English and Thai language support
- 📦 **Standalone Executable** - Pre-built Windows executable available (`gui.exe`)

## Installation

### Option 1: Standalone Executable (Windows)

1. Download `gui.exe` from releases
2. Create a `keymap.json` file (see Configuration section)
3. Double-click `gui.exe` to run

### Option 2: Python Installation

#### Prerequisites

- Python 3.8 or higher
- pip package manager

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/keegang6705/midi-player-for-games.git
cd midi-player-for-games
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the GUI:
```bash
python gui.py
```

## Usage

### GUI Interface

1. **Select a Keymap** - Drop-down menu at the top to choose your key mapping profile
2. **Browse MIDI Files** - Files displayed with duration and compatibility status:
   - ✓ Green - Note range is compatible
   - ⚠ Orange - Note range mismatch (will be adjusted per settings)
   - Gray - File has no notes
3. **Preview File Info** - Shows duration and compatibility before playing
4. **Adjust Settings** - Settings tab includes:
   - Language selection
   - Playback speed (multiplier or target duration)
   - Range handling mode
   - Window always-on-top toggle
   - Countdown duration (0-10 seconds)
   - MIDI directory management
5. **Play** - Click "Play" to start playback with countdown, "Stop" to halt
6. **Test Keymap** - Verify all key bindings are working correctly

### Key Binding Hints

- **Add Directory** - Browse button or Settings → Directory section
- **Change Language** - Settings tab → Language dropdown (requires restart)
- **Remove Directory** - Settings tab → Directory section → Remove button

## Configuration

### keymap.json

Define your key mappings in `keymap.json`. Each mapping is a profile with MIDI note numbers mapped to keyboard keys.

Example:
```json
{
  "piano": {
    "60": "z",
    "61": "x",
    "62": "c",
    "63": "v",
    "64": "b",
    "65": "shift+z",
    "66": "ctrl+z"
  },
  "rhythm_game": {
    "48": "a",
    "49": "s",
    "50": "d",
    "51": "f",
    "52": "space"
  }
}
```

**Note:** MIDI notes range from 0-127. Use the format `modifier+key` for key combinations.

Supported keys:
- Letters: `a-z`
- Numbers: `0-9`
- Special: `space`, `enter`, `tab`, `backspace`, `escape`, `delete`, `insert`
- Arrow keys: `up`, `down`, `left`, `right`
- Navigation: `home`, `end`, `pageup`, `pagedown`
- Function: `f1-f12`

Supported modifiers:
- `shift+key`
- `ctrl+key`
- `alt+key`
- Multiple: `ctrl+shift+key`

### settings.json

Settings are automatically created and managed through the GUI. Manual editing is supported:

```json
{
    "selected_keymap": "piano",
    "range_mismatch_handling": 1,
    "speed_multiplier": 1.0,
    "target_duration": null,
    "playback_mode": 0,
    "midi_directories": ["C:/Users/User/Music", "D:/GameMidi"],
    "selected_language": "en",
    "window_topmost": true,
    "countdown_duration": 3
}
```

**Settings explanation:**
- `selected_keymap` - Currently active key mapping
- `playback_mode` - `0` for speed multiplier, `1` for target duration
- `speed_multiplier` - Playback speed (1.0 = normal, 2.0 = 2x faster)
- `target_duration` - Playback duration in seconds (overrides speed_multiplier when used)
- `range_mismatch_handling` - How to handle notes outside keymap range:
  - `1` - **Scale** - Stretch all notes to fit range (preserves note relationships)
  - `2` - **Nearest Key** - Map each note to closest available key
  - `3` - **Discard** - Skip notes outside range
  - `4` - **Align Low** - Shift all notes up to fit minimum key
  - `5` - **Align High** - Shift all notes down to fit maximum key
  - `6` - **Optimal** - Find best subrange of MIDI notes that fits keymap
- `midi_directories` - List of directories containing MIDI files
- `selected_language` - `en` (English) or `th` (Thai)
- `window_topmost` - Keep window on top of other windows (requires restart)
- `countdown_duration` - Seconds before playback starts (0-10)

## Class API

Use the `MidiPlayer` class in your own Python projects:

```python
from midiplayer import MidiPlayer

# Initialize
player = MidiPlayer()

# Get available keymaps
keymaps = player.get_keymaps_list()

# Set keymap
player.set_keymap("piano")

# Get current keymap
current_keymap = player.get_current_keymap()

# List MIDI files
files = player.list_midi_files()

# Get MIDI file info
info = player.get_midi_info("song.mid")
# Returns: {'filename': 'song.mid', 'duration': 120.5, 'note_range': (36, 96), 'has_notes': True}

# Play MIDI with callbacks
def progress_callback(percentage):
    print(f"Progress: {percentage}%")

def status_callback(status):
    print(f"Status: {status}")

player.play_midi("song.mid", on_progress=progress_callback, on_status=status_callback)

# Test keymap
player.test_keymap(on_progress=lambda c,t: print(f"{c}/{t}"), on_status=status_callback)

# Configure playback
player.set_playback_speed(speed_multiplier=1.5)
player.set_playback_speed(target_duration=180)  # Play in 3 minutes

# Manage directories
player.add_midi_directory("D:/Music/GameMidi")
player.remove_midi_directory("D:/Music/GameMidi")

# Check MIDI compatibility
compatibility = player.check_midi_range("song.mid")
# Returns: 'compatible', 'no_notes', or mismatch details
```

## Building Executable

To build the Windows standalone executable:

```bash
pip install pyinstaller
pyinstaller gui.spec
```

The executable will be in the `dist/gui/` folder.

## Troubleshooting

### Keys not pressing
- Ensure the game window is focused
- Administrator/UAC privileges may be required
- Try adjusting playback speed (slower might help)
- Use "Test Keymap" to verify bindings work
- Check if key combinations are supported in the game

### MIDI file not playing
- Verify the file is a valid MIDI file (.mid or .midi)
- Check if notes are within your keymap's range (shown in file info)
- Try a different range handling mode
- Some MIDI files may have no playable notes

### Timing issues / notes skipped
- Close unnecessary applications to free up CPU
- Try reducing playback speed
- Check antivirus/security software isn't interfering
- Ensure game window has focus (key events need focus)

### Language not changing
- Changing language requires restarting the application
- Go to Settings → Language and restart the app

## Performance Notes

- The player uses high-precision timing for smooth playback
- Key events are sent via Windows scancodes (most compatible with games)
- Timing accuracy is better with fewer background applications
- Very fast playback speeds (>3x) may cause timing jitter

## Support & Feedback

- 💝 **Donate**: Support development at [keegang.cc/donate](https://keegang.cc/donate)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/keegang6705/midi-player-for-games/issues)
- ⭐ **Star**: If you find this useful, please star the repository!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 2.1
- Improved playback timing accuracy
- Better time drift handling during playback
- Reduced timing jitter for smoother key presses

### Version 2.0
- Full PyQt5 GUI redesign
- Support for multiple MIDI directories
- 6 range handling modes
- Multi-language support (English, Thai)
- Countdown timer customization
- Window always-on-top option

### Version 1.0
- Initial console-based release

## Built With

- [Mido](https://github.com/mido/mido) - MIDI file handling
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Python ctypes](https://docs.python.org/3/library/ctypes.html) - Windows key event simulation

---

Made with ❤️ by [keegang6705](https://github.com/keegang6705)
