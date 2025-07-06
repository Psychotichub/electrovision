# 🎯 ElectroVision AI Training Data Guide

## 📋 Quick Overview

Your AI model needs **labeled images** of electrical plans to learn component detection. Here's how to get started:

## 🎯 Target Components (9 Classes)

| Class ID | Component | Examples | Annotation Tips |
|----------|-----------|----------|-----------------|
| 0 | **switch** | Light switches, toggle switches | Include switch symbol + mounting box |
| 1 | **outlet** | Electrical outlets, GFCI receptacles | Include outlet slots + ground symbols |
| 2 | **light** | Light fixtures, ceiling lights, lamps | Include entire fixture symbol |
| 3 | **panel** | Electrical panels, distribution boards | Include panel outline + labels |
| 4 | **wire** | Wires, cables, conduits | Annotate wire segments |
| 5 | **junction** | Wire junctions, connection points | Mark clear connection dots |
| 6 | **breaker** | Circuit breakers, fuses | Include rating labels if visible |
| 7 | **ground** | Ground symbols, earth connections | Include complete ground symbol |
| 8 | **measurement** | Voltage/amperage measurements | Include entire measurement text |

## 🚀 Data Collection Options

### 🌟 Option 1: Use Your DWG/PDF Files (⭐ RECOMMENDED)
**Convert your real electrical plans directly to training data!**

```bash
# 1. Place files in source directories:
source_files/pdf/     ← Your PDF electrical plans
source_files/dwg/     ← Your AutoCAD DWG files  
source_files/dxf/     ← Your DXF files

# 2. Convert to training images
python prepare_training_data.py

# 3. Annotate the extracted images
pip install labelImg
labelImg dataset/images/train dataset/labels/train
```

**Why this is best:**
- ✅ **90-95% accuracy** on your specific drawing styles
- ✅ **Learns your symbols** and component representations
- ✅ **Handles your quality** (scanned, CAD, mixed formats)
- ✅ **Automatic organization** into train/validation sets

📖 **See `DWG_PDF_TRAINING_GUIDE.md` for detailed instructions**  
🚀 **See `QUICK_START_EXAMPLE.md` for step-by-step example**

### Option 2: Use Existing Electrical Plans 
```
✅ Your company's CAD drawings
✅ Public domain electrical schematics
✅ Educational electrical diagrams
✅ Sample DWG/DXF files from online
```

### Option 3: Generate Sample Data
```
🎨 Run: python get_sample_data.py (creates 15 synthetic plans)
🎨 Online electrical diagram generators
🎨 AI-generated floor plans
🎨 Modified existing plans
```

### Option 4: Download Public Datasets
```
🌐 Open Images Dataset (filtered for electrical)
🌐 COCO Dataset (electrical annotations)
🌐 Academic research datasets
🌐 Government building plan databases
```

## 📁 File Structure Required

```
dataset/
├── images/
│   ├── train/              # 70-80% of data
│   │   ├── plan_001.jpg
│   │   ├── plan_002.png
│   │   └── ...
│   └── val/                # 20-30% of data
│       ├── plan_val_001.jpg
│       └── ...
└── labels/
    ├── train/              # Corresponding labels
    │   ├── plan_001.txt
    │   ├── plan_002.txt
    │   └── ...
    └── val/                # Validation labels
        ├── plan_val_001.txt
        └── ...
```

## 🏷️ Label Format (YOLO)

Each `.txt` file contains bounding box annotations:
```
class_id center_x center_y width height
0 0.5 0.3 0.1 0.1
1 0.2 0.7 0.15 0.12
```

**Values are normalized (0.0 to 1.0):**
- `center_x, center_y`: Object center position
- `width, height`: Object dimensions
- All coordinates relative to image size

## 🛠️ Recommended Annotation Tools

### 1. **LabelImg** (Free, Easy)
```bash
pip install labelImg
labelImg
```
- Select directory: `dataset/images/train`
- Change save format to "YOLO"
- Draw bounding boxes around components
- Choose correct class from dropdown

### 2. **CVAT** (Online, Collaborative)
- Visit: https://cvat.org
- Upload images
- Create annotation project
- Download in YOLO format

### 3. **Roboflow** (Advanced, Paid)
- Visit: https://roboflow.com
- Dataset management + augmentation
- Auto-annotation features
- Export to YOLO format

## 📊 Dataset Size Recommendations

| Dataset Size | Use Case | Expected Performance |
|--------------|----------|---------------------|
| **50-100 images** | Proof of concept | 60-70% accuracy |
| **200-500 images** | Development | 75-85% accuracy |
| **1000+ images** | Production | 85-95% accuracy |

## 🎨 Data Augmentation (Automatic)

Your training script automatically applies:
- ✅ Random rotations
- ✅ Brightness/contrast changes  
- ✅ Horizontal flipping
- ✅ Mosaic augmentation
- ✅ Mixup augmentation

## ⚡ Quick Start Commands

### 1. Add Your Images
```bash
# Copy electrical plan images to:
cp your_plans/*.jpg dataset/images/train/
cp your_plans/*.png dataset/images/train/
```

### 2. Annotate with LabelImg
```bash
pip install labelImg
labelImg dataset/images/train dataset/labels/train
```

### 3. Start Training
```bash
python train.py
```

## 🔍 Sample File Examples

### Image File Names:
```
electrical_plan_001.jpg
floor_plan_bedroom.png
circuit_diagram_kitchen.pdf (converted to .jpg)
autocad_export_office.png
```

### Label File Content (plan_001.txt):
```
0 0.5 0.3 0.1 0.1     # switch at center-left
1 0.8 0.2 0.15 0.12   # outlet at top-right  
2 0.4 0.7 0.08 0.08   # light fixture
3 0.1 0.9 0.2 0.15    # electrical panel
```

## 🎯 Pro Tips

1. **Start Small**: Begin with 20-50 well-annotated images
2. **Consistent Quality**: Better to have fewer high-quality annotations
3. **Diverse Sources**: Mix different plan styles and formats
4. **Check Guidelines**: Use `annotation_guidelines.json` for reference
5. **Validate Data**: Review annotations before training

## 🚨 Common Issues

❌ **"No training images found"**
- Solution: Add `.jpg/.png` files to `dataset/images/train/`

❌ **"No labels found"**  
- Solution: Create `.txt` files in `dataset/labels/train/`

❌ **"Class index out of range"**
- Solution: Ensure class IDs are 0-8 in label files

❌ **"Images and labels mismatch"**
- Solution: Each image needs corresponding `.txt` file

## 📞 Need Help?

- Check `annotation_guidelines.json` for detailed component descriptions
- Review YOLO annotation format documentation
- Test with small dataset first (10-20 images)
- Verify file naming matches exactly

---

🎉 **Ready to train your ElectroVision AI model!** Start with a small dataset and gradually expand as you see results. 