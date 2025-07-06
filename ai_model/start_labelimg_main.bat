@echo off
echo Starting LabelImg from Main Python Installation...
echo ElectroVision AI - 91 Class Electrical Component Annotation
echo ========================================================
cd /d "E:\ElectroVision AI\ai_model\dataset\images\train"
echo Current directory: %CD%
echo Starting LabelImg with 91 electrical component classes...
"C:\Users\sures\AppData\Roaming\Python\Python310\Scripts\labelImg.exe"
echo LabelImg closed.
pause 