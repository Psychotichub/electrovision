# LabelImg Usage Guide for ElectroVision AI

## 🎯 Quick Start

### 1. Launch LabelImg
```bash
cd "ai_model/dataset/images/train"
python -m labelImg
```

### 2. Setup Directories
- **Open Dir**: `E:\ElectroVision AI\ai_model\dataset\images\train`
- **Change Save Dir**: `E:\ElectroVision AI\ai_model\dataset\labels\train`
- **Classes File**: `E:\ElectroVision AI\ai_model\dataset\classes.txt`

## 📋 Labeling Process

### Step-by-Step Instructions

1. **Select Format**: Choose YOLO or Pascal VOC
2. **Load Image**: Click on image or use A/D keys
3. **Create Box**: Press `W` and drag around object
4. **Add Label**: Type class name from classes.txt
5. **Save**: Press `Ctrl+S`
6. **Next Image**: Press `D`

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `W` | Create rectangle |
| `A` | Previous image |
| `D` | Next image |
| `Del` | Delete selected box |
| `Ctrl+S` | Save annotation |
| `Ctrl+D` | Copy current label |
| `Space` | Flag as verified |
| `Ctrl+U` | Load all images |

## 🏷️ Class Labels

Use these predefined classes for consistency:

1. **electrical_component** - General electrical parts
2. **circuit_board** - PCBs and electronic boards
3. **wire** - Individual wires and cables
4. **connector** - Plugs, sockets, terminals
5. **resistor** - Resistive components
6. **capacitor** - Capacitive components
7. **transformer** - Transformers and inductors
8. **switch** - Switches and buttons
9. **led** - LEDs and indicators
10. **fuse** - Fuses and circuit protection
11. **relay** - Relays and contactors
12. **terminal** - Terminal blocks
13. **junction_box** - Electrical boxes
14. **cable** - Cable assemblies
15. **conduit** - Cable conduits and raceways

## 📁 File Structure

```
ai_model/dataset/
├── images/
│   ├── train/          <- Your training images
│   └── val/            <- Validation images
├── labels/
│   ├── train/          <- Training annotations (auto-saved here)
│   └── val/            <- Validation annotations
├── classes.txt         <- Class definitions
└── LABELING_GUIDE.md   <- This guide
```

## 💡 Best Practices

### Quality Guidelines

1. **Tight Bounding Boxes**: Draw boxes close to object edges
2. **Complete Objects**: Include entire visible object
3. **Consistent Labeling**: Use same class names consistently
4. **No Overlapping**: Avoid overlapping bounding boxes
5. **Clear Visibility**: Only label clearly visible objects

### Annotation Tips

- **Start with easy images** to get familiar with the tool
- **Save frequently** to avoid losing work
- **Use consistent class names** from the classes.txt file
- **Review your work** by cycling through labeled images
- **Flag completed images** with spacebar

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Can't see bounding box | Press `Ctrl+H` to toggle visibility |
| Wrong class name | Double-click box to edit label |
| Accidentally deleted box | Press `Ctrl+Z` to undo |
| Image too small | Use mouse wheel to zoom |
| Can't save | Check save directory permissions |

## 🚀 Workflow Optimization

### Recommended Workflow

1. **Batch Setup**: Set directories once
2. **Consistent Sessions**: Label in focused 30-60 minute sessions
3. **Regular Breaks**: Take breaks to maintain accuracy
4. **Quality Check**: Review every 10-20 images
5. **Backup**: Regularly backup your labels folder

### Progress Tracking

- **Total Images**: ~100+ in train folder
- **Target**: Label all training images
- **Quality**: Aim for consistent, accurate boxes
- **Validation**: Also label validation images when ready

## 📊 Output Formats

### YOLO Format (Recommended)
- **File**: `train_img_001.txt`
- **Format**: `class_id x_center y_center width height`
- **Coordinates**: Normalized (0-1 range)

### Pascal VOC Format
- **File**: `train_img_001.xml`
- **Format**: XML with detailed metadata
- **Coordinates**: Absolute pixel values

## 🔧 Troubleshooting

### If LabelImg Crashes
```bash
# Re-run the application
cd "ai_model/dataset/images/train"
python -m labelImg
```

### If Annotations Don't Save
1. Check save directory exists
2. Verify write permissions
3. Ensure proper format selected

### Common Errors
- **Path issues**: Use absolute paths
- **Permission errors**: Run as administrator if needed
- **Format mismatch**: Ensure YOLO/VOC format consistency

---

**Happy Labeling! 🎯**

Remember: Quality over quantity - accurate labels are crucial for model performance. 