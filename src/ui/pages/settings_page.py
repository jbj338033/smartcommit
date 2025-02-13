from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox
from PyQt6.QtCore import pyqtSignal
from src.config.settings import Settings

class SettingsPage(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("설정")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        
        back_btn = QPushButton("뒤로")
        back_btn.clicked.connect(self.back_clicked)
        header.addWidget(back_btn)
        layout.addLayout(header)

        api_layout = QVBoxLayout()
        api_layout.addWidget(QLabel("OpenAI API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.settings.get('openai_api_key', ''))
        self.api_key_input.setPlaceholderText("sk-...")
        api_layout.addWidget(self.api_key_input)
        layout.addLayout(api_layout)

        lang_layout = QVBoxLayout()
        lang_layout.addWidget(QLabel("커밋 메시지 언어:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(['ko', 'en'])
        self.language_combo.setCurrentText(self.settings.get('language', 'ko'))
        lang_layout.addWidget(self.language_combo)
        layout.addLayout(lang_layout)

        save_btn = QPushButton("설정 저장")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

    def save_settings(self):
        api_key = self.api_key_input.text().strip()
        if not api_key.startswith('sk-'):
            QMessageBox.warning(self, '경고', 'OpenAI API 키는 sk-로 시작해야 합니다.')
            return

        self.settings.set('openai_api_key', api_key)
        self.settings.set('language', self.language_combo.currentText())
        
        QMessageBox.information(self, '성공', '설정이 저장되었습니다.')
        self.back_clicked.emit()