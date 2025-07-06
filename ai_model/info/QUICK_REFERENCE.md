# 🚀 LabelImg Quick Reference Card

## Essential Shortcuts
- `W` = Create box
- `A` = Previous image  
- `D` = Next image
- `Del` = Delete box
- `Ctrl+S` = Save
- `Space` = Mark verified

## Setup (Do Once)
1. **Open Dir**: `E:\ElectroVision AI\ai_model\dataset\images\train`
2. **Save Dir**: `E:\ElectroVision AI\ai_model\dataset\labels\train`
3. **Format**: Select YOLO
4. **Classes**: Load `classes.txt`

## Labeling Steps
1. Press `W` → Drag box around object
2. Type class name (see classes.txt)
3. Press `Ctrl+S` to save
4. Press `D` for next image

## Classes (Copy/Paste)
- electrical_component
- circuit_board
- wire
- connector
- resistor
- capacitor
- transformer
- switch
- led
- fuse
- relay
- terminal
- junction_box
- cable
- conduit

## File Locations
- **Images**: `ai_model/dataset/images/train/`
- **Labels**: `ai_model/dataset/labels/train/`
- **Classes**: `ai_model/dataset/classes.txt`

## Quality Tips
✅ Tight boxes around objects
✅ Complete visible objects
✅ Consistent class names
✅ Save frequently
❌ No overlapping boxes
❌ No partially visible objects 