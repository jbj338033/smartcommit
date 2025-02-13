from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
from src.config.settings import Settings
from src.ui.pages.project_select_page import ProjectSelectPage
from src.ui.pages.commit_page import CommitPage
from src.ui.pages.settings_page import SettingsPage

class MainWindow(QMainWindow):
   def __init__(self, settings: Settings):
       super().__init__()
       self.settings = settings
       self.init_ui()

   def init_ui(self):
       self.setWindowTitle('Git Commit Manager')
       self.setMinimumSize(1000, 700)
       self.setContentsMargins(0, 0, 0, 0)

       self.stack = QStackedWidget()
       self.setCentralWidget(self.stack)

       self.project_page = ProjectSelectPage(self.settings)
       self.commit_page = CommitPage(self.settings)
       self.settings_page = SettingsPage(self.settings)

       self.stack.addWidget(self.project_page)
       self.stack.addWidget(self.commit_page)
       self.stack.addWidget(self.settings_page)

       self.project_page.project_selected.connect(self.on_project_selected)
       self.commit_page.show_settings.connect(self.show_settings)
       self.settings_page.back_clicked.connect(self.show_commit_page)

       self.apply_styles()

   def apply_styles(self):
       self.setStyleSheet("""
           QMainWindow {
               background-color: #f8f9fa;
           }
           QPushButton {
               background-color: #2196F3;
               color: white;
               border: none;
               padding: 10px 20px;
               border-radius: 6px;
               min-width: 120px;
               font-size: 14px;
               font-weight: bold;
           }
           QPushButton:hover {
               background-color: #1976D2;
           }
           QPushButton:pressed {
               background-color: #1565C0;
           }
           QPushButton:disabled {
               background-color: #BDBDBD;
           }
           QLineEdit, QComboBox {
               padding: 10px;
               border: 2px solid #e0e0e0;
               border-radius: 6px;
               font-size: 14px;
               background: white;
           }
           QLineEdit:focus, QComboBox:focus {
               border-color: #2196F3;
           }
           QComboBox::drop-down {
               border: none;
               padding-right: 10px;
           }
           QComboBox::down-arrow {
               image: none;
               border-left: 5px solid transparent;
               border-right: 5px solid transparent;
               border-top: 5px solid #666;
               margin-right: 5px;
           }
           QLabel {
               color: #212529;
               font-size: 14px;
           }
           QCheckBox {
               font-size: 14px;
               spacing: 8px;
           }
           QCheckBox::indicator {
               width: 18px;
               height: 18px;
               border: 2px solid #e0e0e0;
               border-radius: 4px;
               background: white;
           }
           QCheckBox::indicator:checked {
               background-color: #2196F3;
               border-color: #2196F3;
               image: url(check.png);
           }
           QCheckBox::indicator:hover {
               border-color: #2196F3;
           }
           QScrollBar:vertical {
               border: none;
               background: #f8f9fa;
               width: 10px;
               margin: 0;
           }
           QScrollBar::handle:vertical {
               background: #c1c9d0;
               border-radius: 5px;
               min-height: 20px;
           }
           QScrollBar::add-line:vertical,
           QScrollBar::sub-line:vertical {
               border: none;
               background: none;
           }
       """)

   def on_project_selected(self, path: str):
       self.commit_page.set_project(path)
       self.stack.setCurrentWidget(self.commit_page)

   def show_settings(self):
       self.stack.setCurrentWidget(self.settings_page)

   def show_commit_page(self):
       self.stack.setCurrentWidget(self.commit_page)