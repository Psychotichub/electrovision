@echo off
echo Starting LabelImg for ElectroVision AI...
cd /d "E:\ElectroVision AI\ai_model\dataset\images\train"
call "E:\ElectroVision AI\.venv\Scripts\activate.bat"
"C:\Users\sures\AppData\Roaming\Python\Python310\Scripts\labelImg.exe"
pause 