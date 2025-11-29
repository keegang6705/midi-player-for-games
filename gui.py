import sys
import os
import webbrowser
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QLabel,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox, QProgressBar,
    QTabWidget, QGroupBox, QFormLayout, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from midiplayer import MidiPlayer
from languages import translate


class PlaybackThread(QThread):
    status_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    playback_finished = pyqtSignal(bool)
    
    def __init__(self, player, filename):
        super().__init__()
        self.player = player
        self.filename = filename
    
    def run(self):
        result = self.player.play_midi(self.filename, self.on_progress, self.on_status)
        self.playback_finished.emit(result)
    
    def on_progress(self, msg_index):
        self.progress_updated.emit(msg_index)
    
    def on_status(self, status):
        self.status_changed.emit(status)


class TestThread(QThread):
    status_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int)
    test_finished = pyqtSignal(bool)
    
    def __init__(self, player):
        super().__init__()
        self.player = player
    
    def run(self):
        result = self.player.test_keymap(self.on_progress, self.on_status)
        self.test_finished.emit(result)
    
    def on_progress(self, current, total):
        self.progress_updated.emit(current, total)
    
    def on_status(self, status):
        self.status_changed.emit(status)


class MidiPlayerGUI(QMainWindow):
    def __init__(self, lang='en'):
        super().__init__()
        self.lang = lang
        self.player = None
        self.playback_thread = None
        self.test_thread = None
        self.init_player()
        self.init_ui()
    
    def init_player(self):
        try:
            self.player = MidiPlayer()
        except Exception as e:
            QMessageBox.critical(self, translate('msg_error', self.lang), f"{translate('msg_init_failed', self.lang)}: {e}")
            sys.exit(1)
    
    def init_ui(self):
        self.setWindowTitle(translate('app_title', self.lang))
        self.setGeometry(100, 100, 500, 800)
        icon_path = os.path.join(os.path.dirname(__file__), 'keegang.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet(self.get_stylesheet())
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setElideMode(Qt.ElideRight)
        tabs.addTab(self.create_player_tab(), translate('tab_player', self.lang))
        tabs.addTab(self.create_settings_tab(), translate('tab_settings', self.lang))
        tabs.addTab(self.create_about_tab(), translate('tab_about', self.lang))
        main_layout.addWidget(tabs)
        self.status_label = QLabel(translate('ready', self.lang))
        status_font = QFont()
        status_font.setPointSize(10)
        self.status_label.setFont(status_font)
        main_layout.addWidget(self.status_label)
    
    def create_player_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        keymap_layout = QHBoxLayout()
        keymap_label = QLabel(translate('label_keymap', self.lang))
        keymap_font = QFont()
        keymap_font.setPointSize(11)
        keymap_label.setFont(keymap_font)
        keymap_layout.addWidget(keymap_label)
        self.keymap_combo = QComboBox()
        self.keymap_combo.setFont(QFont(None, 11))
        self.keymap_combo.addItems(self.player.get_keymaps_list())
        current = self.player.get_keymap_name()
        if current:
            self.keymap_combo.setCurrentText(current)
        self.keymap_combo.currentTextChanged.connect(self.on_keymap_changed)
        keymap_layout.addWidget(self.keymap_combo)
        keymap_layout.addStretch()
        layout.addLayout(keymap_layout)
        list_label = QLabel(translate('label_midi_files', self.lang))
        list_font = QFont()
        list_font.setPointSize(11)
        list_label.setFont(list_font)
        layout.addWidget(list_label)
        self.midi_list = QListWidget()
        self.midi_list.setFont(QFont(None, 10))
        self.refresh_midi_list()
        self.midi_list.itemSelectionChanged.connect(self.on_midi_selected)
        layout.addWidget(self.midi_list, stretch=1)
        self.info_label = QLabel(translate('label_select_file', self.lang))
        info_font = QFont()
        info_font.setPointSize(10)
        self.info_label.setFont(info_font)
        layout.addWidget(self.info_label)
        button_layout = QHBoxLayout()
        self.play_btn = QPushButton(translate('btn_play', self.lang))
        self.play_btn.setFont(QFont(None, 11))
        self.play_btn.setMinimumHeight(40)
        self.play_btn.clicked.connect(self.on_play)
        button_layout.addWidget(self.play_btn)
        self.stop_btn = QPushButton(translate('btn_stop', self.lang))
        self.stop_btn.setFont(QFont(None, 11))
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        test_btn = QPushButton(translate('btn_test_keymap', self.lang))
        test_btn.setFont(QFont(None, 11))
        test_btn.setMinimumHeight(40)
        test_btn.clicked.connect(self.on_test_keymap)
        button_layout.addWidget(test_btn)
        browse_btn = QPushButton(translate('btn_browse', self.lang))
        browse_btn.setFont(QFont(None, 11))
        browse_btn.setMinimumHeight(40)
        browse_btn.clicked.connect(self.on_browse_folder)
        button_layout.addWidget(browse_btn)
        layout.addLayout(button_layout)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        return widget
    
    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lang_layout = QHBoxLayout()
        lang_label = QLabel(translate('label_language', self.lang))
        lang_label.setFont(QFont(None, 11))
        lang_combo = QComboBox()
        lang_combo.setFont(QFont(None, 11))
        lang_combo.setMaximumWidth(150)
        lang_combo.addItems(['English', 'Thai'])
        current_lang = 0 if self.lang == 'en' else 1
        lang_combo.setCurrentIndex(current_lang)
        lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        speed_group = QGroupBox(translate('group_speed', self.lang))
        speed_group.setFont(QFont(None, 12))
        speed_layout = QFormLayout()
        mode_group = QButtonGroup()
        speed_radio = QRadioButton(translate('mode_speed_mult', self.lang))
        speed_radio.setFont(QFont(None, 10))
        duration_radio = QRadioButton(translate('mode_target_dur', self.lang))
        duration_radio.setFont(QFont(None, 10))
        mode_group.addButton(speed_radio, 0)
        mode_group.addButton(duration_radio, 1)
        playback = self.player.get_playback_speed()
        if playback.get('target_duration'):
            duration_radio.setChecked(True)
        else:
            speed_radio.setChecked(True)
        speed_layout.addRow(speed_radio)
        speed_layout.addRow(duration_radio)
        self.speed_multiplier = QDoubleSpinBox()
        self.speed_multiplier.setFont(QFont(None, 11))
        self.speed_multiplier.setMinimum(0.1)
        self.speed_multiplier.setMaximum(4.0)
        self.speed_multiplier.setSingleStep(0.1)
        self.speed_multiplier.setValue(playback["speed_multiplier"])
        self.speed_multiplier.valueChanged.connect(self.on_speed_changed)
        self.speed_multiplier.setEnabled(speed_radio.isChecked())
        self.target_duration = QDoubleSpinBox()
        self.target_duration.setFont(QFont(None, 11))
        self.target_duration.setMinimum(0.1)
        self.target_duration.setMaximum(600.0)
        self.target_duration.setSingleStep(1.0)
        if playback.get('target_duration'):
            self.target_duration.setValue(playback['target_duration'])
        self.target_duration.setEnabled(duration_radio.isChecked())
        self.target_duration.valueChanged.connect(self.on_target_duration_changed)
        mode_group.buttonClicked.connect(lambda b: self.on_playback_mode_changed(mode_group.id(b)))
        speed_label = QLabel(translate('label_speed', self.lang))
        speed_label.setFont(QFont(None, 11))
        speed_layout.addRow(speed_label, self.speed_multiplier)
        dur_label = QLabel(translate('label_duration', self.lang))
        dur_label.setFont(QFont(None, 11))
        speed_layout.addRow(dur_label, self.target_duration)
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        range_group = QGroupBox(translate('group_range', self.lang))
        range_group.setFont(QFont(None, 12))
        range_layout = QFormLayout()
        self.range_combo = QComboBox()
        self.range_combo.setFont(QFont(None, 11))
        self.range_combo.addItems([
            translate('mode_scale', self.lang),
            translate('mode_nearest', self.lang),
            translate('mode_discard', self.lang)
        ])
        self.range_combo.setCurrentIndex(self.player.get_range_mismatch_handling() - 1)
        self.range_combo.currentIndexChanged.connect(self.on_range_changed)
        range_label = QLabel(translate('label_mode', self.lang))
        range_label.setFont(QFont(None, 11))
        range_layout.addRow(range_label, self.range_combo)
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        dir_group = QGroupBox(translate('group_directory', self.lang))
        dir_group.setFont(QFont(None, 12))
        dir_layout = QVBoxLayout()
        self.dir_list = QListWidget()
        self.dir_list.setFont(QFont(None, 10))
        self.dir_list.setMaximumHeight(120)
        self.dir_list.itemSelectionChanged.connect(self.on_dir_selected)
        self.refresh_dir_list()
        dir_layout.addWidget(self.dir_list)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(translate('btn_add_dir', self.lang))
        add_btn.setFont(QFont(None, 10))
        add_btn.clicked.connect(self.on_add_directory)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton(translate('btn_remove_dir', self.lang))
        remove_btn.setFont(QFont(None, 10))
        remove_btn.clicked.connect(self.on_remove_directory)
        btn_layout.addWidget(remove_btn)
        dir_layout.addLayout(btn_layout)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        layout.addStretch()
        return widget
    
    def create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel(translate('about_title', self.lang))
        title_font = QFont()
        title_font.setPointSize(20)
        title.setFont(title_font)
        layout.addWidget(title)
        desc = QLabel(translate('about_desc', self.lang))
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc.setFont(desc_font)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        github_btn = QPushButton(translate('btn_github', self.lang))
        github_btn.setFont(QFont(None, 12))
        github_btn.setMinimumHeight(40)
        github_btn.clicked.connect(lambda: webbrowser.open("https://github.com/keegang6705/midi-player-for-games"))
        layout.addWidget(github_btn)
        donate_btn = QPushButton(translate('btn_donate', self.lang))
        donate_btn.setFont(QFont(None, 12))
        donate_btn.setMinimumHeight(45)
        donate_btn.setStyleSheet("QPushButton { background-color: #3299a2; color: white; font-weight: bold; padding: 10px; border-radius: 5px; } QPushButton:hover { background-color: #E55555; }")
        donate_btn.clicked.connect(lambda: webbrowser.open("https://keegang.cc/donate"))
        layout.addWidget(donate_btn)
        layout.addStretch()
        return widget
    
    def get_stylesheet(self):
        """Get the application stylesheet."""
        return """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 10px 25px;
                border: 1px solid #3d3d3d;
                margin-right: 3px;
                font-size: 11pt;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #4CAF50;
            }
            QGroupBox {
                color: #e0e0e0;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 11pt;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #4CAF50;
                border: 1px solid #3d3d3d;
            }
            QListWidget {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QLabel {
                color: #e0e0e0;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                font-size: 11pt;
            }
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """
    
    def refresh_midi_list(self):
        self.midi_list.clear()
        files = self.player.list_midi_files()
        for filename in files:
            info = self.player.get_midi_info(filename)
            if 'error' not in info:
                duration = f"{int(info['duration'] // 60):02d}:{int(info['duration'] % 60):02d}"
                display_text = f"{filename} ({duration})"
            else:
                display_text = f"{filename} (error)"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, filename)
            self.midi_list.addItem(item)
    
    def refresh_dir_list(self):
        self.dir_list.clear()
        for directory in self.player.get_midi_directories():
            item = QListWidgetItem(directory)
            self.dir_list.addItem(item)
    
    def on_keymap_changed(self, keymap_name):
        if keymap_name:
            self.player.set_keymap(keymap_name)
            self.refresh_midi_list()
            self.update_info_label()
    
    def on_midi_selected(self):
        self.update_info_label()
    
    def on_dir_selected(self):
        pass
    
    def update_info_label(self):
        if not self.midi_list.currentItem():
            self.info_label.setText("Select a MIDI file")
            return
        filename = self.midi_list.currentItem().data(Qt.UserRole)
        info = self.player.get_midi_info(filename)
        if 'error' in info:
            self.info_label.setText(f"Error: {info['error']}")
            return
        duration = f"{int(info['duration'] // 60):02d}:{int(info['duration'] % 60):02d}"
        range_check = self.player.check_midi_range(filename)
        if range_check == 'compatible':
            status = "✓ Compatible"
            color = "green"
        elif range_check == 'no_notes':
            status = "No notes"
            color = "gray"
        else:
            status = "⚠ Range mismatch"
            color = "orange"
        info_text = f"<b>{filename}</b><br>Duration: {duration}<br><span style='color:{color};'>{status}</span>"
        self.info_label.setText(info_text)
    
    def on_play(self):
        if not self.midi_list.currentItem():
            QMessageBox.warning(self, translate('msg_warning', self.lang), translate('msg_select_file', self.lang))
            return
        if not self.player.get_current_keymap():
            QMessageBox.warning(self, translate('msg_warning', self.lang), translate('msg_select_keymap', self.lang))
            return
        filename = self.midi_list.currentItem().data(Qt.UserRole)
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.playback_thread = PlaybackThread(self.player, filename)
        self.playback_thread.status_changed.connect(self.on_status_changed)
        self.playback_thread.playback_finished.connect(self.on_playback_finished)
        self.playback_thread.start()
    
    def on_stop(self):
        self.player.stop_playback = True
        self.stop_btn.setEnabled(False)
    
    def on_test_keymap(self):
        if not self.player.get_current_keymap():
            QMessageBox.warning(self, translate('msg_warning', self.lang), translate('msg_select_keymap', self.lang))
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.test_thread = TestThread(self.player)
        self.test_thread.status_changed.connect(self.on_status_changed)
        self.test_thread.progress_updated.connect(self.on_test_progress)
        self.test_thread.test_finished.connect(self.on_test_finished)
        self.test_thread.start()
    
    def on_add_directory(self):
        folder = QFileDialog.getExistingDirectory(self, translate('btn_browse', self.lang))
        if folder:
            if self.player.add_midi_directory(folder):
                self.refresh_dir_list()
                self.refresh_midi_list()
                self.status_label.setText(f"Added: {folder}")
            else:
                QMessageBox.warning(self, translate('msg_error', self.lang), translate('msg_error_invalid_dir', self.lang))
    
    def on_remove_directory(self):
        if not self.dir_list.currentItem():
            return
        directory = self.dir_list.currentItem().text()
        if self.player.remove_midi_directory(directory):
            self.refresh_dir_list()
            self.refresh_midi_list()
            self.status_label.setText(f"Removed: {directory}")
    
    def on_browse_folder(self):
        self.on_add_directory()
    
    def on_speed_changed(self, value):
        self.player.set_playback_speed(speed_multiplier=value)
    
    def on_target_duration_changed(self, value):
        self.player.set_playback_speed(target_duration=value)
    
    def on_playback_mode_changed(self, mode_id):
        if mode_id == 0:
            self.speed_multiplier.setEnabled(True)
            self.target_duration.setEnabled(False)
        else:
            self.speed_multiplier.setEnabled(False)
            self.target_duration.setEnabled(True)
    
    def on_language_changed(self, index):
        new_lang = 'en' if index == 0 else 'th'
        if new_lang != self.lang:
            self.lang = new_lang
            self.player.settings['selected_language'] = new_lang
            self.player.save_settings()
            QMessageBox.information(self, "Info", "Restart app to apply language change")
    
    def on_range_changed(self, index):
        self.player.set_range_mismatch_handling(index + 1)
    
    def on_status_changed(self, status):
        self.status_label.setText(status)
    
    def on_playback_finished(self, completed):
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    def on_test_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current + 1)
    
    def on_test_finished(self, completed):
        self.progress_bar.setVisible(False)
        if completed:
            QMessageBox.information(self, translate('msg_success', self.lang), translate('msg_test_complete', self.lang))


def main():
    app = QApplication(sys.argv)
    lang = 'en'
    if os.path.exists('settings.json'):
        try:
            import json
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                lang = settings.get('selected_language', 'en')
        except:
            pass
    else:
        player = MidiPlayer()
        player.save_settings()
    gui = MidiPlayerGUI(lang=lang)
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
