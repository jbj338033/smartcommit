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
        
        # 스택 위젯 설정
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 페이지 생성
        self.project_page = ProjectSelectPage(self.settings)
        self.commit_page = CommitPage(self.settings)
        self.settings_page = SettingsPage(self.settings)
        
        # 스택에 페이지 추가
        self.stack.addWidget(self.project_page)
        self.stack.addWidget(self.commit_page)
        self.stack.addWidget(self.settings_page)
        
        # 시그널 연결
        self.project_page.project_selected.connect(self.on_project_selected)
        self.commit_page.show_settings.connect(self.show_settings)
        self.settings_page.back_clicked.connect(self.show_commit_page)
        
        # 스타일 적용
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QCheckBox {
                font-size: 14px;
            }
        """)

    def on_project_selected(self, path: str):
        self.commit_page.set_project(path)
        self.stack.setCurrentWidget(self.commit_page)

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_page)

    def show_commit_page(self):
        self.stack.setCurrentWidget(self.commit_page)
