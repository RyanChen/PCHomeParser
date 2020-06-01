import requests
import os

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    CurrentPath = sys._MEIPASS
except Exception:
    CurrentPath = os.path.abspath(".")

os.makedirs('./img/',exist_ok=True)

def SaveImg(url, name):
    r = requests.get(url)
    with open('./img/' + name + '.jpg','wb') as f:
        #將圖片下載下來
        f.write(r.content)
        file_path = os.path.join(CurrentPath, "img", name + ".jpg")
        return file_path
