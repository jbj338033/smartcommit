from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel, QScrollArea
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from typing import List, Tuple
from pathlib import Path

class FileListWidget(QWidget):
   files_selected = pyqtSignal(list)

   def __init__(self):
       super().__init__()
       self.checkboxes = []
       self.init_ui()

   def init_ui(self):
       main_layout = QVBoxLayout(self)
       main_layout.setContentsMargins(0, 0, 0, 0)
       main_layout.setSpacing(10)

       header = QHBoxLayout()
       header.setContentsMargins(10, 10, 10, 0)

       self.refresh_btn = QPushButton("새로고침")
       self.refresh_btn.setStyleSheet("""
           QPushButton {
               background-color: #4CAF50;
               color: white;
               border: none;
               padding: 8px 15px;
               border-radius: 4px;
               font-weight: bold;
           }
           QPushButton:hover {
               background-color: #388E3C;
           }
       """)
       self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
       self.refresh_btn.clicked.connect(self.refresh_requested)
       header.addWidget(self.refresh_btn)

       self.select_all_cb = QCheckBox("전체 선택")
       self.select_all_cb.setStyleSheet("QCheckBox { padding: 5px; }")
       self.select_all_cb.stateChanged.connect(self.toggle_all)
       header.addWidget(self.select_all_cb)

       self.auto_refresh_cb = QCheckBox("자동 새로고침")
       self.auto_refresh_cb.setStyleSheet("QCheckBox { padding: 5px; }")
       self.auto_refresh_cb.setChecked(True)
       self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
       header.addWidget(self.auto_refresh_cb)
       
       header.addStretch()
       main_layout.addLayout(header)

       scroll_area = QScrollArea()
       scroll_area.setWidgetResizable(True)
       scroll_area.setStyleSheet("""
           QScrollArea {
               border: 1px solid #ddd;
               border-radius: 4px;
               background: white;
           }
       """)

       scroll_content = QWidget()
       self.files_layout = QVBoxLayout(scroll_content)
       self.files_layout.setSpacing(5)
       self.files_layout.setContentsMargins(10, 10, 10, 10)
       self.files_layout.addStretch()
       
       scroll_area.setWidget(scroll_content)
       main_layout.addWidget(scroll_area)

       self.refresh_timer = QTimer(self)
       self.refresh_timer.timeout.connect(self.refresh_requested)
       self.refresh_timer.start(3000)

   def refresh_requested(self):
       if hasattr(self.parent(), 'update_file_list'):
           self.parent().update_file_list()

   def toggle_auto_refresh(self, state):
       if state:
           self.refresh_timer.start(3000)
       else:
           self.refresh_timer.stop()

   def set_files(self, files: List[Tuple[str, str, str]]):
       selected_files = self.get_selected_files()
       
       for cb in self.checkboxes:
           cb.deleteLater()
       self.checkboxes.clear()
       
       while self.files_layout.count():
           item = self.files_layout.takeAt(0)
           if item.widget():
               item.widget().deleteLater()
           elif item.layout():
               while item.layout().count():
                   child = item.layout().takeAt(0)
                   if child.widget():
                       child.widget().deleteLater()

       for file_path, status, change_type in sorted(files, key=lambda x: x[0].lower()):
           file_widget = QWidget()
           file_widget.setStyleSheet("""
               QWidget {
                   border-radius: 4px;
                   padding: 5px;
               }
               QWidget:hover {
                   background-color: #f5f5f5;
               }
           """)
           
           file_layout = QHBoxLayout(file_widget)
           file_layout.setContentsMargins(5, 5, 5, 5)
           
           cb = QCheckBox(str(Path(file_path).name))
           cb.setProperty('full_path', file_path)
           cb.setProperty('change_type', change_type)
           
           if file_path in [f[0] for f in selected_files]:
               cb.setChecked(True)

           status_colors = {
               'deleted': ('#dc3545', '삭제됨'),
               'modified': ('#ffc107', '수정됨'),
               'renamed': ('#17a2b8', '이름변경'),
               'untracked': ('#28a745', '새파일')
           }
           color, status_text = status_colors.get(status, ('#6c757d', status))
           
           file_layout.addWidget(cb)
           file_layout.addWidget(QLabel(f"({status_text})"))
           
           path_label = QLabel(str(Path(file_path).parent))
           path_label.setStyleSheet(f"color: {color}; font-size: 12px;")
           file_layout.addWidget(path_label)
           file_layout.addStretch()

           self.files_layout.insertWidget(self.files_layout.count() - 1, file_widget)
           self.checkboxes.append(cb)
           cb.stateChanged.connect(self.update_selected_files)

       self.update_select_all_state()

   def toggle_all(self, state):
       for cb in self.checkboxes:
           cb.setChecked(state)

   def update_selected_files(self):
       selected = [(cb.property('full_path'), cb.property('change_type'))
                  for cb in self.checkboxes if cb.isChecked()]
       self.files_selected.emit(selected)
       self.update_select_all_state()

   def update_select_all_state(self):
       if not self.checkboxes:
           self.select_all_cb.setChecked(False)
       else:
           checked = sum(1 for cb in self.checkboxes if cb.isChecked())
           self.select_all_cb.setChecked(checked == len(self.checkboxes))

   def get_selected_files(self) -> List[Tuple[str, str]]:
       return [(cb.property('full_path'), cb.property('change_type'))
               for cb in self.checkboxes if cb.isChecked()]