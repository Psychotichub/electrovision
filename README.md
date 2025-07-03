# ⚡ ElectroVision AI

**AI-Powered Electrical Plan Interpreter for PDF, DWG, and DXF files**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

## 🎯 Overview

ElectroVision AI is an intelligent system that analyzes electrical plans from PDF, DWG, and DXF files. It uses advanced AI techniques including computer vision and natural language processing to:

- **Extract electrical components** (switches, outlets, lights, panels, etc.)
- **Analyze wiring paths** and connections
- **Perform compliance checking** against electrical codes
- **Enable natural language queries** about electrical plans
- **Generate detailed reports** and visualizations

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** and npm
- **Tesseract OCR** (for text extraction from scanned PDFs)
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/psychotic/electrovision-ai.git
   cd electrovision-ai
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**
   ```bash
   cd backend
   npm start
   ```

5. **Start the frontend (in a new terminal)**
   ```bash
   cd frontend
   npm start
   ```

6. **Open your browser** to `http://localhost:3001`

## 🏗️ Architecture

```
ElectroVision AI/
├── 🎨 frontend/          # React web application
├── 🔧 backend/           # Node.js API server
├── 🤖 ai_model/          # YOLO training scripts
├── 📊 data-prep/         # Data processing utilities
├── 🐍 backend/python/    # Python analysis scripts
└── 📁 uploads/           # File upload directory
```

## 📋 Features

### 🔍 File Processing
- **PDF Analysis**: Extract text and images from electrical plans
- **DWG/DXF Support**: Convert CAD files to analyzable formats
- **OCR Integration**: Handle scanned documents with Tesseract
- **Multi-format Support**: Process various electrical plan formats

### 🤖 AI Analysis
- **Component Detection**: YOLOv8-based object detection
- **Text Recognition**: Advanced OCR with preprocessing
- **Connection Analysis**: Graph-based wiring path detection
- **Classification**: Intelligent component categorization

### 📊 Visualization
- **Interactive Dashboard**: Real-time analysis results
- **Component Mapping**: Visual representation of detected elements
- **Statistics**: Comprehensive analysis metrics
- **Export Options**: JSON, PDF, and image outputs

### 🔧 API Features
- **RESTful API**: Clean, documented endpoints
- **Real-time Updates**: WebSocket support for live analysis
- **File Validation**: Secure upload with format checking
- **Error Handling**: Comprehensive error reporting

## 🎯 Usage Examples

### Basic File Analysis

1. **Upload a file** through the web interface
2. **Wait for processing** (typically 10-30 seconds)
3. **View results** in the dashboard
4. **Export data** in your preferred format

### Advanced Queries

```javascript
// Example API call
fetch('http://localhost:3000/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Analysis results:', data);
});
```

### Training Custom Models

```bash
# Prepare your dataset
python data-prep/extract_from_pdf.py /path/to/pdfs /path/to/output

# Convert CAD files
python data-prep/format_converter.py /path/to/cad /path/to/output

# Train the model
cd ai_model
python train.py
```

## 🔧 Configuration

### Backend Configuration (`.env`)

```env
PORT=3000
NODE_ENV=development
UPLOAD_DIR=uploads
PYTHON_CMD=python
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=.pdf,.dwg,.dxf
CORS_ORIGIN=http://localhost:3001
LOG_LEVEL=info
```

### AI Model Configuration (`ai_model/config.yaml`)

```yaml
# Training parameters
epochs: 100
batch_size: 16
img_size: 640
workers: 8

# Model architecture
model: 'yolov8n.pt'
pretrained: true

# Dataset paths
train: dataset/images/train
val: dataset/images/val

# Classes (12 electrical components)
nc: 12
names: ['switch', 'outlet', 'light', 'panel', 'wire', 'junction', 
        'breaker', 'ground', 'measurement', 'motor', 'transformer', 'sensor']
```

## 📊 API Documentation

### Upload Endpoint
```http
POST /upload
Content-Type: multipart/form-data

Response:
{
  "status": "success",
  "data": {
    "analysis_type": "pdf_electrical_plan",
    "detected_components": [...],
    "text_content": "...",
    "statistics": {...}
  }
}
```

### Health Check
```http
GET /
Response: {
  "message": "ElectroVision AI Backend is running!",
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 🧠 AI Model Details

### Component Detection Classes

| Class ID | Component | Description |
|----------|-----------|-------------|
| 0 | Switch | Light switches, toggle switches |
| 1 | Outlet | Electrical outlets, sockets |
| 2 | Light | Light fixtures, lamps |
| 3 | Panel | Electrical panels, distribution boards |
| 4 | Wire | Electrical wires, cables |
| 5 | Junction | Wire junctions, connection points |
| 6 | Breaker | Circuit breakers, fuses |
| 7 | Ground | Ground symbols, earth connections |
| 8 | Measurement | Voltage, amperage readings |
| 9 | Motor | Electric motors, fans |
| 10 | Transformer | Transformers, converters |
| 11 | Sensor | Sensors, detectors |

### Training Process

1. **Data Collection**: Gather electrical plan images
2. **Annotation**: Use LabelImg or CVAT for labeling
3. **Preprocessing**: Enhance images for better detection
4. **Training**: Use YOLOv8 with transfer learning
5. **Validation**: Test on validation dataset
6. **Export**: Convert to ONNX for production

## 📁 Data Preparation

### PDF Processing
```bash
python data-prep/extract_from_pdf.py \
  --input-dir /path/to/pdfs \
  --output-dir /path/to/extracted \
  --train-split 0.8
```

### CAD File Conversion
```bash
python data-prep/format_converter.py \
  --input-dir /path/to/cad \
  --output-dir /path/to/converted \
  --format cad
```

### Annotation Tools
- **LabelImg**: Desktop annotation tool
- **CVAT**: Web-based collaborative annotation
- **Roboflow**: Dataset management and augmentation

## 🛠️ Development

### Running in Development Mode

```bash
# Backend with hot reload
cd backend
npm run dev

# Frontend with hot reload
cd frontend
npm start
```

### Running Tests

```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Lint backend
cd backend
npm run lint

# Lint frontend
cd frontend
npm run lint

# Python code formatting
black data-prep/ ai_model/
```

## 🚨 Troubleshooting

### Common Issues

**1. Python dependencies not installing**
```bash
# Try upgrading pip
pip install --upgrade pip
pip install -r requirements.txt
```

**2. Tesseract not found**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Download from GitHub releases
```

**3. Node.js modules not installing**
```bash
# Clear npm cache
npm cache clean --force
npm install
```

**4. CUDA/GPU issues**
```bash
# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"

# Install CPU-only version if needed
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Performance Optimization

- **Use GPU**: Install CUDA-enabled PyTorch for faster training
- **Increase batch size**: If you have more GPU memory
- **Use smaller models**: YOLOv8n for faster inference
- **Enable caching**: Set `cache=True` in training config

## 📈 Roadmap

### Version 1.1
- [ ] 3D visualization with Three.js
- [ ] BIM integration support
- [ ] Multi-language plan support
- [ ] Advanced compliance checking

### Version 1.2
- [ ] Real-time collaboration features
- [ ] Mobile app support
- [ ] Cloud deployment options
- [ ] Advanced analytics dashboard

### Version 2.0
- [ ] SCADA system integration
- [ ] AR/VR visualization
- [ ] IoT device connectivity
- [ ] Automated report generation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Reporting Issues
Please use the [GitHub Issues](https://github.com/psychotic/electrovision-ai/issues) page to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Psychotic** - Project Lead & AI Development
- **Community Contributors** - Various improvements and features

## 🙏 Acknowledgments

- **Ultralytics** for the amazing YOLOv8 framework
- **OpenCV** community for computer vision tools
- **React** team for the fantastic frontend framework
- **PyMuPDF** for PDF processing capabilities
- **ezdxf** for CAD file handling

## 📞 Support

- 📧 Email: support@electrovision-ai.com
- 💬 Discord: [Join our community](https://discord.gg/electrovision-ai)
- 📖 Documentation: [docs.electrovision-ai.com](https://docs.electrovision-ai.com)
- 🐛 Issues: [GitHub Issues](https://github.com/psychotic/electrovision-ai/issues)

---

**Made with ❤️ by the ElectroVision AI team** 