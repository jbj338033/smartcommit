import os
import sys
import platform
from setuptools import setup, find_packages

def build_executable():
    os_type = platform.system().lower()
    
    if os_type == 'darwin':  # macOS
        os.system('pip install -r requirements.txt')
        os.system('pip install pyinstaller')
        os.system('pyinstaller --name SmartCommit '
                 '--windowed '
                 '--icon=assets/icon.icns '
                 '--add-data "assets:assets" '
                 '--onefile '
                 'src/main.py')
        
        # Create DMG (requires create-dmg tool)
        os.system('brew install create-dmg')
        os.system('create-dmg '
                 '--volname "SmartCommit Installer" '
                 '--window-pos 200 120 '
                 '--window-size 800 400 '
                 '--icon-size 100 '
                 '--icon "SmartCommit.app" 200 190 '
                 '--hide-extension "SmartCommit.app" '
                 '--app-drop-link 600 185 '
                 'SmartCommit.dmg '
                 'dist/SmartCommit.app')
        
    elif os_type == 'windows':  # Windows
        os.system('pip install -r requirements.txt')
        os.system('pip install pyinstaller')
        os.system('pyinstaller --name SmartCommit '
                 '--windowed '
                 '--icon=assets/icon.ico '
                 '--add-data "assets;assets" '
                 '--onefile '
                 'src/main.py')
        
        # Create Windows installer using Inno Setup
        inno_script = """
[Setup]
AppName=SmartCommit
AppVersion=0.1.0
DefaultDirName={pf}\\SmartCommit
DefaultGroupName=SmartCommit
OutputDir=output
OutputBaseFilename=SmartCommit_Setup

[Files]
Source: "dist\\SmartCommit.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\SmartCommit"; Filename: "{app}\\SmartCommit.exe"
Name: "{commondesktop}\\SmartCommit"; Filename: "{app}\\SmartCommit.exe"
        """
        
        with open('installer.iss', 'w') as f:
            f.write(inno_script)
        
        os.system('"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" installer.iss')

if __name__ == '__main__':
    build_executable()