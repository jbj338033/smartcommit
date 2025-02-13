from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QComboBox, QMessageBox)
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

        # 헤더
        header = QHBoxLayout()
        title = QLabel("설정")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        
        back_btn = QPushButton("뒤로")
        back_btn.clicked.connect(self.back_clicked)
        header.addWidget(back_btn)
        layout.addLayout(header)

        # OpenAI API Key
        api_layout = QVBoxLayout()
        api_layout.addWidget(QLabel("OpenAI API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.settings.get('openai_api_key', ''))
        self.api_key_input.setPlaceholderText("sk-...")
        api_layout.addWidget(self.api_key_input)
        layout.addLayout(api_layout)

        # 언어 설정
        lang_layout = QVBoxLayout()
        lang_layout.addWidget(QLabel("커밋 메시지 언어:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(['ko', 'en'])
        self.language_combo.setCurrentText(self.settings.get('language', 'ko'))
        lang_layout.addWidget(self.language_combo)
        layout.addLayout(lang_layout)

        # 커밋 메시지 포맷
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("커밋 메시지 포맷:"))
        format_layout.addWidget(QLabel("({message}는 자동 생성된 메시지로 대체됩니다)"))
        self.format_input = QLineEdit()
        self.format_input.setText(self.settings.get('commit_format', 'feat: {message}'))
        format_layout.addWidget(self.format_input)
        layout.addLayout(format_layout)

        # 저장 버튼
        save_btn = QPushButton("설정 저장")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

    def save_settings(self):
        # API 키 검증
        api_key = self.api_key_input.text().strip()
        if not api_key.startswith('sk-'):
            QMessageBox.warning(self, '경고', 'OpenAI API 키는 sk-로 시작해야 합니다.')
            return

        # 커밋 포맷 검증
        commit_format = self.format_input.text().strip()
        if '{message}' not in commit_format:
            QMessageBox.warning(self, '경고', '커밋 포맷에는 {message}가 포함되어야 합니다.')
            return

        # 설정 저장
        self.settings.set('openai_api_key', api_key)
        self.settings.set('language', self.language_combo.currentText())
        self.settings.set('commit_format', commit_format)

        QMessageBox.information(self, '성공', '설정이 저장되었습니다.')
        self.back_clicked.emit()