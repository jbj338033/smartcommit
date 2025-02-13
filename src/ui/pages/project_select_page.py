from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                        QFileDialog, QListWidget, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from src.config.settings import Settings
from pathlib import Path

class ProjectSelectPage(QWidget):
   project_selected = pyqtSignal(str)

   def __init__(self, settings: Settings):
       super().__init__()
       self.settings = settings
       self.init_ui()

   def init_ui(self):
       layout = QVBoxLayout(self)
       layout.setSpacing(20)
       layout.setContentsMargins(30, 30, 30, 30)

       title = QLabel("Git Commit Manager")
       title.setStyleSheet("""
           font-size: 32px;
           font-weight: bold;
           color: #2196F3;
           margin: 20px 0;
       """)
       title.setAlignment(Qt.AlignmentFlag.AlignCenter)
       layout.addWidget(title)

       select_btn = QPushButton("프로젝트 디렉토리 선택")
       select_btn.setStyleSheet("""
           QPushButton {
               background-color: #2196F3;
               color: white;
               border: none;
               padding: 15px;
               border-radius: 8px;
               font-size: 16px;
               min-width: 200px;
           }
           QPushButton:hover {
               background-color: #1976D2;
           }
       """)
       select_btn.clicked.connect(self.select_project)
       select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
       layout.addWidget(select_btn, alignment=Qt.AlignmentFlag.AlignCenter)

       recent_header = QHBoxLayout()
       recent_label = QLabel("최근 프로젝트")
       recent_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
       recent_header.addWidget(recent_label)
       
       clear_btn = QPushButton("목록 지우기")
       clear_btn.setStyleSheet("""
           QPushButton {
               color: #666;
               border: none;
               padding: 5px;
               font-size: 12px;
           }
           QPushButton:hover {
               color: #333;
           }
       """)
       clear_btn.clicked.connect(self.clear_recent_list)
       recent_header.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
       layout.addLayout(recent_header)

       self.recent_list = QListWidget()
       self.recent_list.setStyleSheet("""
           QListWidget {
               background-color: white;
               border: 1px solid #ddd;
               border-radius: 8px;
               padding: 10px;
           }
           QListWidget::item {
               padding: 10px;
               border-bottom: 1px solid #eee;
           }
           QListWidget::item:hover {
               background-color: #f5f5f5;
           }
           QListWidget::item:selected {
               background-color: #e3f2fd;
               color: #2196F3;
           }
       """)
       self.recent_list.itemDoubleClicked.connect(self.on_recent_selected)
       layout.addWidget(self.recent_list)
       
       self.update_recent_list()
       layout.addStretch()

   def update_recent_list(self):
       self.recent_list.clear()
       recent_projects = self.settings.get('recent_projects', [])
       for project in recent_projects:
           path = Path(project)
           if path.exists() and path.is_dir():
               self.recent_list.addItem(str(path))

   def select_project(self):
       dir_path = QFileDialog.getExistingDirectory(
           self,
           "프로젝트 디렉토리 선택",
           str(Path.home()),
           QFileDialog.Option.ShowDirsOnly
       )
       if dir_path:
           self.settings.add_recent_project(dir_path)
           self.project_selected.emit(dir_path)

   def on_recent_selected(self, item):
       path = Path(item.text())
       if path.exists() and path.is_dir():
           self.project_selected.emit(str(path))
       else:
           self.settings.remove_recent_project(item.text())
           self.update_recent_list()

   def clear_recent_list(self):
       self.settings.clear_recent_projects()
       self.update_recent_list()