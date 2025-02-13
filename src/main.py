import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.config.settings import Settings

def main():
    app = QApplication(sys.argv)
    settings = Settings()
    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()