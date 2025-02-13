from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel
from PyQt6.QtCore import pyqtSignal, QTimer
from typing import List, Tuple

class FileListWidget(QWidget):
    files_selected = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.checkboxes = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 헤더
        header = QHBoxLayout()
        
        # 새로고침 버튼 추가
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                max-width: 80px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_requested)
        header.addWidget(self.refresh_btn)
        
        self.select_all_cb = QCheckBox("전체 선택")
        self.select_all_cb.stateChanged.connect(self.toggle_all)
        header.addWidget(self.select_all_cb)
        
        # 자동 새로고침 체크박스
        self.auto_refresh_cb = QCheckBox("자동 새로고침")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        header.addWidget(self.auto_refresh_cb)
        
        header.addStretch()
        layout.addLayout(header)

        # 파일 목록을 담을 레이아웃
        self.files_layout = QVBoxLayout()
        layout.addLayout(self.files_layout)
        layout.addStretch()

        # 자동 새로고침 타이머 설정
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_requested)
        self.refresh_timer.start(3000)  # 3초마다 새로고침

    def refresh_requested(self):
        """새로고침 요청 시그널 발생"""
        if hasattr(self.parent(), 'update_file_list'):
            self.parent().update_file_list()

    def toggle_auto_refresh(self, state):
        """자동 새로고침 토글"""
        if state:
            self.refresh_timer.start(3000)
        else:
            self.refresh_timer.stop()

    def set_files(self, files: List[Tuple[str, str, str]]):
        # 현재 선택된 파일들 저장
        selected_files = self.get_selected_files()
        
        # 기존 체크박스들 제거
        for cb in self.checkboxes:
            cb.deleteLater()
        self.checkboxes.clear()
        
        # 레이아웃의 모든 아이템 제거
        while self.files_layout.count():
            item = self.files_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        # 새로운 파일 목록 추가
        for file_path, status, change_type in files:
            cb = QCheckBox(file_path)
            # 이전에 선택되었던 파일이면 선택 상태 유지
            if file_path in selected_files:
                cb.setChecked(True)
                
            status_label = QLabel(f"({status})")
            if status == 'deleted':
                status_label.setStyleSheet("color: #dc3545;")  # 빨간색
            elif status == 'modified':
                status_label.setStyleSheet("color: #ffc107;")  # 노란색
            else:
                status_label.setStyleSheet("color: #28a745;")  # 초록색
            
            # change_type을 데이터로 저장
            cb.setProperty('change_type', change_type)
            
            file_layout = QHBoxLayout()
            file_layout.addWidget(cb)
            file_layout.addWidget(status_label)
            file_layout.addStretch()
            
            self.files_layout.addLayout(file_layout)
            self.checkboxes.append(cb)
            cb.stateChanged.connect(self.update_selected_files)
            
    def toggle_all(self, state):
        for cb in self.checkboxes:
            cb.setChecked(state)

    def update_selected_files(self):
        selected = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        self.files_selected.emit(selected)
        self.update_select_all_state()

    def update_select_all_state(self):
        """전체 선택 체크박스 상태 업데이트"""
        if not self.checkboxes:
            self.select_all_cb.setChecked(False)
        else:
            checked = sum(1 for cb in self.checkboxes if cb.isChecked())
            self.select_all_cb.setChecked(checked == len(self.checkboxes))

    def get_selected_files(self) -> List[Tuple[str, str]]:
        """선택된 파일과 change_type 반환"""
        return [(cb.text(), cb.property('change_type')) 
                for cb in self.checkboxes if cb.isChecked()]