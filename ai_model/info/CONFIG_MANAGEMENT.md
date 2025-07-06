# 🎛️ Configuration Management Guide

## ✅ **Answer: YES, config.yaml is the Single Source of Truth!**

You're absolutely correct! The `config.yaml` should be the **single source of truth** for all configuration, including class definitions. Here's the complete solution:

## 🏗️ **Current Architecture**

### **Single Source of Truth**
- **`config.yaml`** - Master configuration file ✅
- Contains all 15 class definitions with descriptions
- Includes training hyperparameters, paths, and settings

### **Auto-Synchronized Files**
- **`classes.txt`** - Master copy (auto-generated)
- **`dataset/classes.txt`** - Dataset copy (auto-generated)
- **`dataset/labels/train/classes.txt`** - LabelImg training (auto-generated)
- **`dataset/labels/val/classes.txt`** - LabelImg validation (auto-generated)

## 🔄 **Sync System**

### **Automatic Sync Tool**
```bash
cd ai_model
python sync_classes.py
```

This script:
- ✅ Reads classes from `config.yaml`
- ✅ Updates all `classes.txt` files automatically
- ✅ Validates synchronization
- ✅ Shows current class definitions

### **When to Sync**
- After modifying class definitions in `config.yaml`
- Before starting LabelImg sessions
- Before training your model
- After pulling updates from git

## 📋 **Class Definition Format**

### **In config.yaml (Master)**
```yaml
# Number of classes
nc: 15

# Class names (single source of truth)
names:
  0: 'main_breaker'            # मुख्य सर्किट ब्रेकर – सम्पूर्ण पावर कट गर्न प्रयोग गरिन्छ
  1: 'mcb'                     # मिनिएचर सर्किट ब्रेकर – ओभरलोड र सर्ट सर्किट सुरक्षा
  2: 'rccb'                    # रेसिडुअल करेन्ट सर्किट ब्रेकर – करेन्ट लीक भएको जाँच्न
  3: 'elcb'                    # अर्थ लीक ब्रेकर – अर्थिङ लीक डिटेक्सन
  4: 'fuse'                    # फ्यूज – ओभर करेन्ट हुँदा जल्ने सुरक्षा यन्त्र
  5: 'distribution_panel'     # पावर वितरण प्यानल – सबै ब्रेकरहरू राखिन्छ
  6: 'busbar'                 # बसबार – पावर ट्रान्सफर गर्न कन्डक्टिव बारहरू
  7: 'isolator'               # आइसोलेटर – मर्मतको लागि लाइन काट्न प्रयोग गरिन्छ
  8: 'contactor'              # कन्ट्याक्टर – मोटर जस्ता लोडहरूको स्विचिङ
  9: 'relay'                  # रिलेज – इलेक्ट्रिकल सिग्नलबाट नियन्त्रण हुने स्विच
  10: 'overload_relay'        # मोटर ओभरलोडबाट जोगाउन प्रयोग हुने सुरक्षा यन्त्र
  11: 'spd'                   # सर्ज प्रोटेक्सन डिभाइस – भोल्टेज स्पाइकबाट रक्षा
  12: 'timer'                 # टाइमर – निश्चित समयपछि स्विच अन/अफ हुने यन्त्र
  13: 'ct'                    # करेन्ट ट्रान्सफर्मर – करेन्ट मापनका लागि
  14: 'pt'                    # भोल्टेज ट्रान्सफर्मर – भोल्टेज मापनका लागि
  15: 'lightning_arrester'    # बिजुलीबाट उपकरण रक्षा गर्ने यन्त्र
  16: 'wire'                  # सामान्य सिंगल वायर – सर्किट जडानको लागि
  17: 'cable'                 # मल्टी-कोर केबल – पावर ट्रान्समिसन
  19: 'conduit'               # पाइप/डक्ट – केबल राख्न प्रयोग हुने
  20: 'cable_tray'            # केबल ट्रे – ठूला केबलहरू सँगठित राख्न प्रयोग हुने
  22: 'pull_box'              # केबल तान्न सजिलो बनाउन प्रयोग हुने बक्स
  23: 'gland'                 # केबललाई उपकरणमा सुरक्षित जडान गर्न
  24: 'lug'                   # केबलको अन्त्यमा राख्ने टर्मिनल
  25: 'busbar_chamber'        # बसबार राख्ने सानो एनक्लोजर
  26: 'switch'                # सामान्य स्विच – सर्किट अन/अफ गर्न
  27: 'dimmer_switch'         # लाइटको ब्राइटनेस नियन्त्रण गर्ने स्विच
  28: 'push_button'           # प्रेस गरेर अन/अफ हुने बटन
  29: 'selector_switch'       # मोड चयन गर्न सकिने स्विच (जस्तै Auto/Manual)
  30: 'limit_switch'          # मेकानिकल मूभमेन्ट डिटेक्ट गर्ने स्विच
  31: 'float_switch'          # पानीको लेभल अनुसार काम गर्ने स्विच
  32: 'rotary_switch'         # घुमाएर मोड परिवर्तन गर्ने स्विच
  33: 'emergency_stop'        # आपतकालीन अवस्थाका लागि स्टप बटन
  34: 'led_light'             # एलईडी लाइट – energy efficient प्रकाश
  35: 'incandescent_bulb'     # परम्परागत फिलामेन्ट बल्ब
  36: 'tube_light'            # लामो ट्यूब आकारको लाइट
  37: 'flood_light'           # ठूला क्षेत्र उज्यालो बनाउन प्रयोग हुने लाइट
  38: 'street_light'          # सडक बत्ती
  39: 'motion_sensor_light'   # गति पत्ता लागेपछि बल्ने लाइट
  40: 'emergency_light'       # पावर गयो भने स्वतः बल्ने लाइट
  42: 'power_socket'          # सामान्य पावर प्लग जडान गर्न
  44: 'industrial_socket'     # उच्च पावर उपकरणका लागि सकेट
  46: 'earth_rod'             # जमिनमा गाडिने अर्थिङ रड
  47: 'earthing_wire'         # अर्थिङमा प्रयोग हुने वायर
  48: 'earth_pit'             # अर्थिङको लागि बनाइने गहिरो खाडल
  49: 'earth_busbar'          # अर्थ कनेक्सनहरूको लागि बसबार
  50: 'earth_terminal'        # उपकरणको अर्थिङ टर्मिनल
  51: 'lightning_protection'  # लाइटनिङ स्ट्राइक रोक्न प्रयोग हुने सिस्टम
  52: 'voltmeter'             # भोल्टेज मापन गर्ने उपकरण
  53: 'ammeter'               # करेन्ट मापन गर्ने उपकरण
  54: 'power_meter'           # पावर मापन गर्ने यन्त्र
  55: 'energy_meter'          # ऊर्जा (kWh) मापन गर्ने यन्त्र
  56: 'multifunction_meter'   # भोल्ट, एम्प, पावर आदि एकै ठाउँमा मापन
  57: 'frequency_meter'       # फ्रिक्वेन्सी (Hz) मापन गर्ने
  58: 'power_factor_meter'    # पावर फैक्टर मापन गर्न प्रयोग हुने यन्त्र
  59: 'plc'                   # प्रोग्रामेबल लोजिक कन्ट्रोलर – अटोमेसनको लागि
  61: 'rtu'                   # रिमोट टर्मिनल युनिट – SCADA मा डेटा पठाउन
  62: 'hmi'                   # मानव-मेसिन इन्टरफेस – PLC सँग इन्टरएक्ट गर्न
  64: 'bms_sensor'            # बिल्डिङ म्यानेजमेन्ट सिस्टमका लागि सेन्सर
  65: 'intercom'              # आन्तरिक संचारका लागि उपकरण
  66: 'wifi_router'           # वायरलेस इन्टरनेट वितरण
  67: 'transformer'           # भोल्टेज बढाउने वा घटाउने उपकरण
  68: 'ups'                   # ब्याकअप पावरका लागि अनइन्टरप्टेबल पावर सप्लाई
  69: 'inverter'              # DC लाई AC मा रूपान्तरण गर्ने
  70: 'battery_bank'          # ब्याकअप पावर स्टोरेज
  71: 'solar_panel'           # सौर्य ऊर्जाबाट बिजुली उत्पादन
  73: 'generator'             # डीजल वा अन्य इन्धनबाट पावर उत्पादन गर्ने
  74: 'motor'                 # इलेक्ट्रिक मोटर
  75: 'vfd'                   # मोटरको स्पीड कन्ट्रोल गर्न प्रयोग हुने ड्राइभ
  76: 'indicator_lamp'        # सिग्नल देखाउने लाइट
  77: 'buzzer'                # साउन्ड अलार्म दिने यन्त्र
  78: 'alarm_system'          # सम्पूर्ण सुरक्षा अलार्म सिस्टम
  79: 'pilot_lamp'            # उपकरण अन/अफ संकेत गर्ने सानो लाइट
  80: 'signal_lamp'           # नियन्त्रण संकेत दिन प्रयोग हुने लाइट
  81: 'fire_alarm_panel'      # फायर सेन्सरहरू नियन्त्रण गर्ने मुख्य प्यानल
  82: 'smoke_detector'        # धुवाँ पत्ता लगाउने सेन्सर
  83: 'heat_detector'         # तापक्रम आधारित फायर डिटेक्सन
  84: 'cctv_camera'           # निगरानी क्यामेरा
  85: 'motion_detector'       # गति पत्ता लगाउने सेन्सर
  86: 'access_control'        # कार्ड वा फिंगरप्रिन्टद्वारा प्रवेश नियन्त्रण
  88: 'name_plate'            # उपकरणमा लगाइने नाम लेखिएको प्लेट
  89: 'label_tag'             # तार वा उपकरण पहिचानको लागि ट्याग
  90: 'circuit_diagram_legend'# इलेक्ट्रिकल सिम्बोलहरूको व्याख्या
  91: 'mounting_frame'        # उपकरणहरू जडान गर्न प्रयोग हुने फ्रेम
  93: 'heat_shrink'           # तार इन्सुलेसनको लागि सुकाउने ट्युब

```

### **In classes.txt (Auto-generated)**
```
electrical_component
circuit_board
wire
connector
resistor
capacitor
transformer
switch
led
fuse
relay
terminal
junction_box
cable
conduit
```

## 🎯 **Best Practices**

### **1. Always Edit config.yaml First**
```yaml
# To add a new class:
nc: 16  # Increment count

names:
  0: 'electrical_component'
  # ... existing classes ...
  15: 'new_class_name'  # Add new class
```

### **2. Run Sync After Changes**
```bash
cd ai_model
python sync_classes.py
```

### **3. Validate Synchronization**
The sync script automatically validates all files are in sync.

### **4. Version Control**
- **Commit**: `config.yaml` (source of truth)
- **Don't commit**: `classes.txt` files (auto-generated)
- **Add to .gitignore**: `classes.txt` files

## 🔧 **Usage Examples**

### **Adding a New Class**
```bash
# 1. Edit config.yaml
nano config.yaml

# 2. Add new class to names section
# 3. Increment nc value
# 4. Sync all files
python sync_classes.py

# 5. Restart LabelImg
cd dataset/images/train
python -m labelImg
```

### **Modifying Existing Classes**
```bash
# 1. Edit class name in config.yaml
# 2. Sync files
python sync_classes.py

# 3. Update existing annotations if needed
# 4. Restart training pipeline
```

### **Validation Check**
```bash
# Check if all files are in sync
python sync_classes.py

# Look for "✅ All files are in sync!" message
```

## 📁 **File Structure**

```
ai_model/
├── config.yaml                    ← MASTER CONFIG ✅
├── sync_classes.py                ← Sync tool
├── classes.txt                    ← Auto-generated
├── dataset/
│   ├── classes.txt               ← Auto-generated
│   └── labels/
│       ├── train/
│       │   └── classes.txt       ← Auto-generated (for LabelImg)
│       └── val/
│           └── classes.txt       ← Auto-generated (for LabelImg)
└── CONFIG_MANAGEMENT.md           ← This guide
```

## 🚀 **Integration with Tools**

### **LabelImg**
- Automatically finds `classes.txt` in labels directories
- No manual setup required after sync
- Classes appear in dropdown automatically

### **Training Pipeline**
- Reads directly from `config.yaml`
- Uses `nc` and `names` sections
- No additional configuration needed

### **Validation Scripts**
- Reference `config.yaml` for class definitions
- Consistent class mapping across all tools

## ⚠️ **Common Pitfalls**

### **❌ Don't Edit classes.txt Directly**
```bash
# Wrong approach:
nano dataset/classes.txt  # ❌ Will be overwritten

# Correct approach:
nano config.yaml          # ✅ Edit source of truth
python sync_classes.py    # ✅ Sync all files
```

### **❌ Don't Forget to Sync**
- Always run `sync_classes.py` after editing `config.yaml`
- LabelImg won't see changes until sync is run

### **❌ Don't Commit Auto-Generated Files**
- Add `classes.txt` to `.gitignore`
- Only commit `config.yaml`

## 🎯 **Summary**

✅ **config.yaml** = Single source of truth  
✅ **classes.txt** = Auto-generated for compatibility  
✅ **sync_classes.py** = Keeps everything in sync  
✅ **Best practice** = Edit config.yaml, then sync  

This approach gives you:
- **Centralized configuration**
- **Tool compatibility** (LabelImg needs classes.txt)
- **Automatic synchronization**
- **Version control friendly**
- **Consistent class definitions**

Perfect configuration management for your ElectroVision AI project! 🎯 