# MIDI Player for Games

A powerful MIDI player designed specifically for playing custom game soundtracks with flexible key mapping and playback control.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-2.0-blue)

## Features

- 🎵 **Multiple Keymap Profiles** - Create and switch between different key mappings for different games
- ⚙️ **Flexible Playback Control** - Adjust playback speed or set target duration
- 📍 **Smart Note Range Handling** - Automatically scale, map, or discard notes that are out of range
- 🎹 **Key Combinations** - Support for modifier keys (Shift, Ctrl, Alt) in key mappings
- 🖥️ **User-Friendly GUI** - Modern PyQt5 interface for easy control
- 📁 **Custom MIDI Directory** - Browse and organize MIDI files in any folder
- ⌨️ **Real-Time Key Mapping** - See exactly which keys will be pressed for each MIDI note
- 🧪 **Keymap Testing** - Test your key mappings before playing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/keegang6705/midi-player-for-games.git
cd midi-player-for-games
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize Windows-specific modules (Windows only):
```bash
python -m pip install --upgrade pywin32
python Scripts/pywin32_postinstall.py -install
```

## Usage

### GUI Mode (Recommended)

Run the GUI application:
```bash
python gui.py
```

#### How to Use:

1. **Select a Keymap** - Choose from available key mapping profiles at the top
2. **Browse MIDI Files** - Your MIDI folder will be displayed with duration and compatibility status
3. **Preview File Info** - See duration and note range compatibility before playing
4. **Adjust Settings** - Modify playback speed and range handling in the Settings tab
5. **Play** - Click "Play" to start playback, "Stop" to stop
6. **Test Keymap** - Click "Test Keymap" to verify your key bindings

### Console Mode

To run the original console-based player:
```bash
python midiplayer_old.py
```

## Configuration

### keymap.json

Define your key mappings in `keymap.json`. Each mapping is a profile with MIDI note numbers mapped to keyboard keys.

Example:
```json
{
  "gaming_profile": {
    "48": "z",
    "49": "x",
    "50": "c",
    "51": "v",
    "52": "b",
    "53": "shift+z",
    "54": "ctrl+z"
  },
  "another_profile": {
    "48": "a",
    "49": "s",
    "50": "d"
  }
}
```

**Note:** MIDI notes range from 0-127. Use the format `modifier+key` for key combinations.

Supported modifiers:
- `shift+key`
- `ctrl+key`
- `alt+key`
- Multiple modifiers: `ctrl+shift+key`

### settings.json

Settings are automatically saved and loaded from `settings.json`. Manual editing is supported:

```json
{
    "selected_keymap": "gaming_profile",
    "range_mismatch_handling": 1,
    "speed_multiplier": 1.0,
    "target_duration": null,
    "midi_directory": "C:/path/to/midi/files"
}
```

**Settings explanation:**
- `selected_keymap` - Currently active key mapping
- `range_mismatch_handling` - How to handle notes outside keymap range:
  - `1` - Scale notes to fit range
  - `2` - Map to nearest available key
  - `3` - Discard out-of-range notes
- `speed_multiplier` - Playback speed (1.0 = normal, 2.0 = 2x faster)
- `target_duration` - Set playback duration in seconds (overrides speed_multiplier)
- `midi_directory` - Directory containing MIDI files

## Class API

### MidiPlayer Class

Use the `MidiPlayer` class in your own Python projects:

```python
from midiplayer import MidiPlayer

# Initialize
player = MidiPlayer()

# Get available keymaps
keymaps = player.get_keymaps_list()

# Set keymap
player.set_keymap("gaming_profile")

# Get current keymap
current_keymap = player.get_current_keymap()

# List MIDI files
files = player.list_midi_files()

# Get MIDI file info
info = player.get_midi_info("song.mid")

# Play MIDI
player.play_midi("song.mid", on_status=print)

# Test keymap
player.test_keymap(on_status=print)

# Configure playback
player.set_playback_speed(speed_multiplier=1.5)
player.set_midi_directory("D:/Music")
```

## Color Indicators (Console Mode)

When listing MIDI files:
- 🟢 **Green** - Note range is compatible with current keymap
- 🟡 **Yellow** - Note range is partially compatible (will be adjusted)
- ⚪ **Gray** - File has no notes
- 🔴 **Red** - Error loading file

## Troubleshooting

### "keymap.json not found"
Ensure `keymap.json` exists in the same directory as the script. Create one with at least one keymap profile.

### Keys not pressing
- Ensure the game window is focused
- Try adjusting playback speed (slower might help)
- Test the keymap first to verify bindings
- Check if key combinations are supported in the game

### MIDI file not playing
- Verify the file is a valid MIDI file (.mid or .midi)
- Check if notes are within your keymap's range
- Try a different range handling mode in settings

### Performance issues
- Close unnecessary applications
- Try reducing playback speed
- Check if your antivirus is interfering

## Support

- 💝 **Donate**: Support development at [keegang.cc/donate](https://keegang.cc/donate)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/keegang6705/midi-player-for-games/issues)
- ⭐ **Star**: If you find this useful, please star the repository!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### Version 2.0
- Refactored to class-based architecture
- Added PyQt5 GUI
- Improved key combination support
- Added progress callbacks
- Better error handling

### Version 1.0
- Initial console-based release

## Acknowledgments

Built with:
- [Mido](https://github.com/mido/mido) - MIDI file handling
- [pynput](https://github.com/moses-palmer/pynput) - Keyboard control
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

---

Made with ❤️ by [keegang6705](https://github.com/keegang6705)
