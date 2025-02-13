import json
from pathlib import Path
from typing import Dict, Any

class Settings:
    def __init__(self):
        self.config_file = Path.home() / '.gitcommitmanager' / 'config.json'
        self.config_file.parent.mkdir(exist_ok=True)
        self.load_settings()

    def load_settings(self):
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                'openai_api_key': '',
                'language': 'ko',
                'commit_format': 'feat: {message}',
                'recent_projects': []
            }
            self.save_settings()

    def save_settings(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save_settings()

    def add_recent_project(self, path: str):
        recent = self.settings.get('recent_projects', [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.settings['recent_projects'] = recent[:5]  # 최근 5개만 유지
        self.save_settings()