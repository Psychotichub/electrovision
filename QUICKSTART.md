# 🚀 ElectroVision AI - Quick Start Guide

Get ElectroVision AI up and running in 5 minutes!

## ⚡ Super Quick Start (One Command)

If you have Python 3.8+ and Node.js 18+ installed:

```bash
# Windows
./run.sh start

# Linux/macOS  
chmod +x run.sh && ./run.sh start
```

That's it! The system will:
1. ✅ Check dependencies
2. ✅ Install packages
3. ✅ Start backend server
4. ✅ Start frontend app
5. ✅ Open browser to http://localhost:3001

## 📋 Prerequisites

### Required Software
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

### Optional (for better OCR)
- **Tesseract OCR** (for scanned PDF analysis)
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt-get install tesseract-ocr`

## 🛠️ Manual Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/psychotic/electrovision-ai.git
cd electrovision-ai
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Backend
```bash
cd backend
npm install
cd ..
```

### Step 4: Setup Frontend
```bash
cd frontend
npm install
cd ..
```

### Step 5: Start Services

**Terminal 1 (Backend):**
```bash
cd backend
npm start
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### Step 6: Open Browser
Navigate to: http://localhost:3001

## 🎯 First Analysis

1. **Upload a file**: Click the upload area or drag & drop
2. **Supported formats**: PDF, DWG, DXF electrical plans
3. **Wait for analysis**: Usually 10-30 seconds
4. **View results**: Components, connections, statistics
5. **Export data**: JSON, images, reports

## 🔧 Troubleshooting

### Backend won't start
```bash
cd backend
npm install
npm start
```

### Frontend won't start
```bash
cd frontend
npm install
npm start
```

### Python errors
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Port conflicts
- Backend uses port 3000
- Frontend uses port 3001
- Kill existing processes: `npx kill-port 3000 3001`

### File upload fails
- Check file size (max 50MB)
- Ensure file format is PDF, DWG, or DXF
- Check backend logs in `logs/backend.log`

## 🚨 Common Issues

**"Python not found"**
- Install Python 3.8+ and add to PATH
- On Windows, check "Add Python to PATH" during installation

**"Node.js not found"**
- Install Node.js 18+ from nodejs.org
- Restart terminal after installation

**"Permission denied"**
- On Linux/macOS: `chmod +x run.sh`
- On Windows: Run PowerShell as Administrator

**"Port already in use"**
```bash
# Kill processes on ports
npx kill-port 3000
npx kill-port 3001
```

**"Module not found"**
```bash
# Reinstall dependencies
cd backend && npm install
cd ../frontend && npm install
pip install -r requirements.txt
```

## 🎉 Success!

You should see:
- ✅ Backend server at http://localhost:3000
- ✅ Frontend app at http://localhost:3001
- ✅ File upload interface
- ✅ Analysis dashboard

## 📚 What's Next?

### Basic Usage
1. Upload electrical plans (PDF/DWG/DXF)
2. View analysis results
3. Export data in various formats

### Advanced Features
- Train custom AI models
- Batch process multiple files
- API integration
- Custom analysis rules

### Training AI Models
```bash
# Prepare training data
python data-prep/extract_from_pdf.py input_folder output_folder

# Train model
cd ai_model
python train.py
```

## 🆘 Need Help?

- 📖 **Full Documentation**: README.md
- 🐛 **Report Issues**: GitHub Issues
- 💬 **Community**: Discord/Forums
- 📧 **Support**: support@electrovision-ai.com

## 🔄 System Commands

```bash
# Start system
./run.sh start

# Stop system
./run.sh stop

# Restart system
./run.sh restart

# Check status
./run.sh status

# Setup only (no start)
./run.sh setup
```

---

**🎯 Goal**: Analyze electrical plans with AI in under 5 minutes!

Happy analyzing! ⚡🚀 