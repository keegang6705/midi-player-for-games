# Language translations for MIDI Player
# Add new languages by creating a new dictionary with language code as key

TRANSLATIONS = {
    'en': {
        'app_title': 'MIDI Player for Games',
        'ready': 'Ready',
        'tab_player': 'Player',
        'tab_settings': 'Settings',
        'tab_about': 'About',
        'label_keymap': 'Keymap:',
        'label_midi_files': 'MIDI Files:',
        'label_select_file': 'Select a MIDI file',
        'label_language': 'Language:',
        'label_speed': 'Speed Multiplier:',
        'label_duration': 'Target Duration (sec):',
        'btn_play': 'Play',
        'btn_stop': 'Stop',
        'btn_test_keymap': 'Test Keymap',
        'btn_browse': 'Browse Folder...',
        'status_duration': 'Duration:',
        'status_compatible': '✓ Compatible',
        'status_no_notes': 'No notes',
        'status_mismatch': '⚠ Range mismatch',
        'group_speed': 'Playback Speed',
        'group_range': 'Range Mismatch Handling',
        'label_mode': 'Mode:',
        'mode_scale': 'Scale notes to fit range',
        'mode_nearest': 'Map to nearest key',
        'mode_discard': 'Discard out of range notes',
        'mode_align_low': 'Align to Low Key',
        'mode_align_high': 'Align to High Key',
        'mode_optimal': 'Find Optimal Range',
        'mode_speed_mult': 'Use Speed Multiplier (0.1x - 4.0x)',
        'mode_target_dur': 'Use Target Duration (seconds)',
        'group_directory': 'MIDI Directory',
        'btn_change': 'Change...',
        'btn_add_dir': 'Add',
        'btn_remove_dir': 'Remove',
        'about_title': 'MIDI Player for Games',
        'about_desc': 'A powerful MIDI player designed for playing custom game soundtracks.\n\nFeatures:\n• Multiple keymap profiles\n• Custom playback speeds\n• Flexible note range handling\n• Real-time key mapping\n• Support for .mid and .midi files',
        'btn_github': 'View on GitHub',
        'btn_donate': 'Support Developer',
        'msg_select_file': 'Please select a MIDI file',
        'msg_select_keymap': 'Please select a keymap',
        'msg_error_invalid_dir': 'Invalid directory',
        'msg_dir_changed': 'Directory changed',
        'msg_test_complete': 'Keymap test completed!',
        'msg_warning': 'Warning',
        'msg_error': 'Error',
        'msg_success': 'Success',
        'msg_init_failed': 'Failed to initialize player',
    },
    'th': {
        'app_title': 'เครื่องเล่น MIDI สำหรับเกม',
        'ready': 'พร้อม',
        'tab_player': 'เล่น',
        'tab_settings': 'การตั้งค่า',
        'tab_about': 'เกี่ยวกับ',

        'label_keymap': 'ผังแป้นพิมพ์:',
        'label_midi_files': 'ไฟล์ MIDI:',
        'label_select_file': 'เลือกไฟล์ MIDI',

        'label_language': 'ภาษา:',
        'label_speed': 'ตัวคูณความเร็ว:',
        'label_duration': 'ระยะเวลาเป้าหมาย (วินาที):',

        'btn_play': 'เล่น',
        'btn_stop': 'หยุด',
        'btn_test_keymap': 'ทดสอบผังแป้นพิมพ์',
        'btn_browse': 'เลือกโฟลเดอร์...',

        'status_duration': 'ความยาว:',
        'status_compatible': 'ใช้งานได้',
        'status_no_notes': 'ไม่มีโน้ต',
        'status_mismatch': 'ช่วงไม่ตรงกัน',

        'group_speed': 'ความเร็วในการเล่น',
        'group_range': 'การจัดการช่วงโน้ตไม่ตรงกัน',

        'label_mode': 'โหมด:',
        'mode_scale': 'ปรับขนาดโน้ตให้พอดีกับช่วง',
        'mode_nearest': 'แมปไปยังคีย์ที่ใกล้ที่สุด',
        'mode_discard': 'ตัดโน้ตที่อยู่นอกช่วงทิ้ง',
        'mode_align_low': 'ชิดแป้นต่ำสุด',
        'mode_align_high': 'ชิดแป้นสูงสุด',
        'mode_optimal': 'หาช่วงที่เหมาะสมที่สุด',
        'mode_speed_mult': 'ใช้โหมดตัวคูณความเร็ว (0.1x - 4.0x)',
        'mode_target_dur': 'ใช้โหมดกำหนดระยะเวลา (วินาที)',

        'group_directory': 'โฟลเดอร์ไฟล์ MIDI',
        'btn_change': 'เปลี่ยน...',
        'btn_add_dir': 'เพิ่ม',
        'btn_remove_dir': 'ลบ',

        'about_title': 'เครื่องเล่น MIDI สำหรับเกม',
        'about_desc':
            'เครื่องเล่น MIDI ที่ออกแบบมาสำหรับใช้กับเสียงประกอบเกมที่กำหนดเอง\n\n'
            'คุณสมบัติ:\n'
            '• รองรับผังแป้นพิมพ์หลายชุด\n'
            '• ปรับความเร็วการเล่นได้\n'
            '• จัดการช่วงโน้ตที่ไม่ตรงกันได้หลายรูปแบบ\n'
            '• แมปปิงคีย์แบบเรียลไทม์\n'
            '• รองรับไฟล์ .mid และ .midi',

        'btn_github': 'เปิดบน GitHub',
        'btn_donate': 'สนับสนุนผู้พัฒนา',

        'msg_select_file': 'กรุณาเลือกไฟล์ MIDI ก่อน',
        'msg_select_keymap': 'กรุณาเลือกผังแป้นพิมพ์',
        'msg_error_invalid_dir': 'โฟลเดอร์ไม่ถูกต้อง',
        'msg_dir_changed': 'เปลี่ยนโฟลเดอร์เรียบร้อยแล้ว',
        'msg_test_complete': 'ทดสอบผังแป้นพิมพ์เสร็จสิ้น',
        'msg_warning': 'คำเตือน',
        'msg_error': 'ข้อผิดพลาด',
        'msg_success': 'สำเร็จ',
        'msg_init_failed': 'ไม่สามารถเริ่มการทำงานของเครื่องเล่นได้',
    }
}

def get_language(lang_code='en'):
    """Get language dictionary, default to English if not found"""
    return TRANSLATIONS.get(lang_code, TRANSLATIONS['en'])

def translate(key, lang_code='en'):
    """Translate a key to the specified language"""
    lang = get_language(lang_code)
    return lang.get(key, key)
