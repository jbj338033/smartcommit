import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QProgressDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from typing import List, Tuple
from src.config.settings import Settings
from src.services.git_service import GitService
from src.services.openai_service import OpenAIService
from src.ui.widgets.file_list_widget import FileListWidget

class CommitWorker(QThread):
    progress = pyqtSignal(str, str)  # (file_path, commit_message)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, git_service: GitService, openai_service: OpenAIService,
                files: List[Tuple[str, str]], commit_format: str, language: str):
        super().__init__()
        self.git_service = git_service
        self.openai_service = openai_service
        self.files = files  # (file_path, change_type) 튜플 리스트
        self.commit_format = commit_format
        self.language = language

    def run(self):
        for file_path, change_type in self.files:
            try:
                # 삭제된 파일의 경우
                if change_type == 'D':
                    commit_message = f"Remove {os.path.basename(file_path)}"
                else:
                    # 파일 내용 읽기 시도
                    try:
                        abs_path = self.git_service.get_absolute_path(file_path)
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        try:
                            with open(abs_path, 'r', encoding='cp949') as f:
                                content = f.read()
                        except:
                            # 바이너리 파일인 경우
                            content = f"Update {os.path.basename(file_path)}"
                    except FileNotFoundError:
                        if change_type == 'D':
                            content = f"Remove {os.path.basename(file_path)}"
                        else:
                            raise

                    # 커밋 메시지 생성
                    commit_message = self.openai_service.generate_commit_message(
                        content, self.language
                    )
                    if not commit_message:
                        commit_message = f"Update {os.path.basename(file_path)}"

                # 커밋 메시지 포맷팅
                formatted_message = self.commit_format.format(message=commit_message)

                # 스테이징
                if not self.git_service.stage_file(file_path, change_type):
                    raise Exception(f"Failed to stage file {file_path}")

                # 커밋
                if not self.git_service.commit(formatted_message):
                    raise Exception(f"Failed to commit file {file_path}")

                self.progress.emit(file_path, formatted_message)

            except Exception as e:
                self.error.emit(f"Error processing {file_path}: {str(e)}")
                continue

        self.finished.emit()
    
class CommitPage(QWidget):
    show_settings = pyqtSignal()

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.git_service = None
        self.openai_service = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 헤더
        header = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(self.path_label)
        
        self.settings_btn = QPushButton("설정")
        self.settings_btn.clicked.connect(self.show_settings)
        header.addWidget(self.settings_btn)
        layout.addLayout(header)

        # 파일 목록
        self.file_list = FileListWidget()
        layout.addWidget(self.file_list)

        # 버튼들
        buttons = QHBoxLayout()
        self.commit_btn = QPushButton("자동 커밋")
        self.commit_btn.clicked.connect(self.commit_selected)
        buttons.addWidget(self.commit_btn)

        self.push_btn = QPushButton("Push")
        self.push_btn.clicked.connect(self.push_changes)
        buttons.addWidget(self.push_btn)
        
        layout.addLayout(buttons)

    def set_project(self, path: str):
        self.path_label.setText(f"프로젝트: {path}")
        
        # Git 서비스 초기화
        self.git_service = GitService(path)
        if not self.git_service.is_git_repo():
            reply = QMessageBox.question(
                self,
                'Git 초기화',
                '선택한 디렉토리는 Git 저장소가 아닙니다. 초기화하시겠습니까?'
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.git_service.init_new_repo()
            else:
                return

        # OpenAI 서비스 초기화
        api_key = self.settings.get('openai_api_key')
        if not api_key:
            QMessageBox.warning(
                self,
                '설정 필요',
                'OpenAI API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 설정해주세요.'
            )
            self.show_settings.emit()
            return

        self.openai_service = OpenAIService(api_key)
        self.update_file_list()
        self.update_push_button()

    def update_file_list(self):
        if self.git_service:
            files = self.git_service.get_unstaged_files()
            self.file_list.set_files(files)

    def update_push_button(self):
        if self.git_service:
            unpushed = len(self.git_service.get_unpushed_commits())
            self.push_btn.setText(f"Push ({unpushed})")
            self.push_btn.setEnabled(unpushed > 0)

    def commit_selected(self):
        files = self.file_list.get_selected_files()
        if not files:
            QMessageBox.warning(self, '경고', '커밋할 파일을 선택해주세요.')
            return

        # 진행 상황 다이얼로그
        progress = QProgressDialog("커밋 진행 중...", "취소", 0, len(files), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(False)
        progress.show()

        # 커밋 워커 시작
        self.commit_worker = CommitWorker(
            self.git_service,
            self.openai_service,
            files,
            self.settings.get('commit_format'),
            self.settings.get('language')
        )

        def on_progress(file_path, commit_message):
            current = progress.value() + 1
            progress.setLabelText(f"커밋 중: {file_path}\n{commit_message}")
            progress.setValue(current)

        def on_error(message):
            QMessageBox.critical(self, '에러', message)
            progress.close()

        def on_finished():
            progress.close()
            self.update_file_list()
            self.update_push_button()
            QMessageBox.information(self, '완료', '모든 파일이 커밋되었습니다.')

        self.commit_worker.progress.connect(on_progress)
        self.commit_worker.error.connect(on_error)
        self.commit_worker.finished.connect(on_finished)
        self.commit_worker.start()

    def push_changes(self):
        try:
            if self.git_service.push():
                QMessageBox.information(self, '성공', '변경사항이 성공적으로 푸시되었습니다.')
                self.update_push_button()
            else:
                QMessageBox.critical(self, '에러', '푸시 중 오류가 발생했습니다.')
        except Exception as e:
            QMessageBox.critical(self, '에러', f'푸시 중 오류가 발생했습니다: {str(e)}')