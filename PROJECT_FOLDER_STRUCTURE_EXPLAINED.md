# 📁 ElectroVision AI: Complete Folder Structure Explained

## 🎯 **Why These Folders Exist**

These folders are **automatically created by your setup.py script** as part of the ElectroVision AI project structure. Each serves a specific purpose in the AI training and analysis workflow.

### 📋 **Complete Folder Breakdown**

## 🗂️ **Data Management Folders**

### 📊 `/data` - **Central Data Hub**
```
data/
├── raw/             ← Original unprocessed data
├── processed/       ← Cleaned and preprocessed data  
└── datasets/        ← Ready-to-train datasets
    ├── train/
    │   ├── images/
    │   └── labels/
    └── val/
        ├── images/
        └── labels/
```

**Purpose**: 
- **Central data repository** for all processing stages
- **Raw data**: Store original electrical plans before processing
- **Processed data**: Store cleaned, enhanced versions
- **Datasets**: YOLO-ready training/validation datasets

### 📁 `/data-prep` - **Data Processing Scripts**
```
data-prep/
├── extract_from_pdf.py    ← PDF data extraction utility
└── format_converter.py    ← Format conversion (DWG→DXF→Images)
```

**Purpose**:
- **Data extraction** from various file formats
- **Format conversion** between CAD formats
- **Preprocessing pipelines** for training data
- **Utility scripts** for data preparation

## 🤖 **AI Model Folders**

### 🧠 `/models` - **Trained AI Models Storage**
```
models/
├── checkpoints/     ← Training checkpoints and saves
└── exports/         ← Final exported models for production
```

**Purpose**:
- **Checkpoints**: Save training progress, resume interrupted training
- **Exports**: Store production-ready models (ONNX, TensorRT, etc.)
- **Version control**: Keep different model versions
- **Backup**: Prevent loss of trained models

### 📈 `/results` - **Training & Analysis Results**
```
results/
├── training_metrics/    ← Loss curves, accuracy plots
├── validation_results/  ← Model performance data
├── analysis_outputs/    ← Component detection results
└── reports/            ← Generated analysis reports
```

**Purpose**:
- **Training metrics**: Loss curves, accuracy graphs
- **Validation results**: Model performance on test data
- **Analysis outputs**: Component detection results from uploads
- **Reports**: Generated PDF/JSON analysis reports

## 🔧 **Operational Folders**

### 📝 `/logs` - **System Logs & Debugging**
```
logs/
├── backend.log          ← Backend server logs
├── training.log         ← AI training logs
├── analysis.log         ← File analysis logs
└── error.log           ← Error tracking
```

**Purpose**:
- **Debugging**: Track errors and issues
- **Performance monitoring**: Server response times
- **Training progress**: Monitor AI training status
- **Audit trail**: Track user uploads and analysis

### 🗃️ `/temp` - **Temporary Processing Files**
```
temp/
├── processing/          ← Temporary analysis files
├── conversions/         ← DWG→DXF conversion temp files
├── extractions/         ← PDF extraction temp files
└── cache/              ← Temporary caches
```

**Purpose**:
- **Processing space**: Temporary files during analysis
- **File conversions**: Intermediate format conversions
- **Cache storage**: Speed up repeated operations
- **Cleanup**: Automatically cleaned after operations

### 📤 `/uploads` - **User File Uploads**
```
uploads/
├── timestamp-file1.pdf  ← Timestamped uploaded files
├── timestamp-file2.dwg
└── extracted_images/    ← Extracted images from uploads
```

**Purpose**:
- **User uploads**: Store files uploaded via frontend
- **Timestamped naming**: Prevent filename conflicts
- **Analysis queue**: Files waiting for AI analysis
- **Backup**: Keep uploaded files for re-analysis

## 🔄 **Workflow Integration**

### **📊 Data Flow Pipeline**
```
1. Upload → /uploads → 2. Process → /temp → 3. Analyze → /results
                   ↓
4. Store Raw → /data/raw → 5. Process → /data/processed → 6. Train → /models
```

### **🎯 AI Training Pipeline**
```
/data/raw → /data-prep/scripts → /data/processed → /data/datasets → AI Training → /models
```

### **📈 Analysis Pipeline**
```
Frontend Upload → /uploads → AI Analysis → /results → Dashboard Display
```

## 🛠️ **How They're Created**

These folders are automatically created by your `setup.py` script:

```python
def setup_directories():
    directories = [
        'data/raw',
        'data/processed', 
        'data/datasets/train/images',
        'data/datasets/train/labels',
        'data/datasets/val/images',
        'data/datasets/val/labels',
        'models/checkpoints',
        'models/exports',
        'logs',
        'results',
        'temp'
    ]
```

## 🎯 **Should You Keep Them?**

### ✅ **Keep These** - Essential for functionality:
- **`/data`** - Core data management
- **`/data-prep`** - Essential processing scripts
- **`/models`** - AI model storage
- **`/uploads`** - User file uploads

### 🤔 **Optional** - Can be recreated as needed:
- **`/logs`** - Recreated when logging starts
- **`/results`** - Recreated when analysis runs
- **`/temp`** - Recreated during processing

### 📋 **Management Tips**

#### **Regular Cleanup**:
```bash
# Clean temporary files
rm -rf temp/*

# Clean old logs (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Archive old results
mv results/ archived_results_$(date +%Y%m%d)/
```

#### **Backup Important Folders**:
```bash
# Backup trained models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Backup processed datasets
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/datasets/
```

## 🎉 **Summary**

These folders create a **professional AI development environment** with:

✅ **Organized data management** - Clear separation of raw, processed, and training data  
✅ **Model versioning** - Safe storage of AI models and checkpoints  
✅ **Processing pipeline** - Dedicated spaces for data preparation  
✅ **User interaction** - Seamless file upload and analysis workflow  
✅ **Debugging support** - Comprehensive logging and temporary storage  
✅ **Production ready** - Structured for scaling and maintenance  

**These folders ensure your ElectroVision AI project is organized, maintainable, and ready for professional development!** 