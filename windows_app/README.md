# Windows yt-dlp GUI App

This is a Windows desktop application that allows you to download videos or audio from the web in any format and quality supported by yt-dlp, with a graphical interface and no terminal windows.

## Features
- Paste video link
- Choose download type (video/audio)
- Choose format (mp4, mp3, flac, etc.)
- Choose quality
- Progress bars for loading and downloading
- Choose destination folder after download
- Option to remember download folder
- Popup to set default download folder for all files

## How to Run

1. **Install Python 3.8+** (if not already installed)
2. **Install dependencies:**
   Open a terminal in this folder and run:
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```sh
   python main.py
   ```

## Packaging for Windows
To create a standalone Windows executable, install PyInstaller and run:
```sh
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```
The executable will be in the `dist` folder.
