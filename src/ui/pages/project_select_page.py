from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                          QFileDialog, QListWidget)
from PyQt6.QtCore import pyqtSignal
from src.config.settings import Settings

class ProjectSelectPage(QWidget):
    project_selected = pyqtSignal(str)

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 제목
        title = QLabel("Git Commit Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        layout.addWidget(title)
        
        # 프로젝트 선택 버튼
        select_btn = QPushButton("프로젝트 디렉토리 선택")
        select_btn.clicked.connect(self.select_project)
        layout.addWidget(select_btn)
        
        # 최근 프로젝트 목록
        layout.addWidget(QLabel("최근 프로젝트:"))
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self.on_recent_selected)
        layout.addWidget(self.recent_list)
        
        self.update_recent_list()
        layout.addStretch()

    def update_recent_list(self):
        self.recent_list.clear()
        recent_projects = self.settings.get('recent_projects', [])
        self.recent_list.addItems(recent_projects)

    def select_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, "프로젝트 디렉토리 선택")
        if dir_path:
            self.settings.add_recent_project(dir_path)
            self.project_selected.emit(dir_path)

    def on_recent_selected(self, item):
        self.project_selected.emit(item.text())