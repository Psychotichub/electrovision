# 🚀 Start ElectroVision AI Servers

## Quick Start (2 Commands)

### Option 1: Start Both Servers Automatically
Run this single command to start both frontend and backend:
```bash
npm run dev
```

### Option 2: Start Servers Manually

**Terminal 1 - Backend Server:**
```bash
cd backend
npm install
npm start
# ✅ Backend running on http://localhost:3000
```

**Terminal 2 - Frontend Server:**
```bash
cd frontend  
npm install
npm start
# ✅ Frontend running on http://localhost:3001
```

## 🔧 Troubleshooting Upload Issues

### 1. Check Backend Server
```bash
# Test if backend is running
curl http://localhost:3000

# Should return:
# {"message":"ElectroVision AI Backend is running!","status":"healthy"}
```

### 2. Check Upload Endpoint
```bash
# Test upload endpoint (should return 400 - no file)
curl -X POST http://localhost:3000/upload

# Should return:
# {"error":"No file uploaded"}
```

### 3. Common Upload Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `❌ Backend server is not running` | Backend not started | Run `cd backend && npm start` |
| `Cannot connect to backend server` | Wrong port/URL | Check http://localhost:3000 |
| `Upload endpoint not found` | Route not configured | Check backend/routes/upload.js |
| `File too large` | File > 50MB | Use smaller files |
| `tesseract is not installed` | OCR not available | See `INSTALL_TESSERACT.md` for setup |
| `PDF parsing failed` | File format issue | Try different PDF or check file integrity |

## 🌐 Server Status

### Backend Server (Port 3000)
- **Health Check**: http://localhost:3000
- **Upload Endpoint**: http://localhost:3000/upload
- **Logs**: Check terminal running `npm start` in backend folder

### Frontend Server (Port 3001)  
- **Web Interface**: http://localhost:3001
- **File Upload**: http://localhost:3001 → drag & drop files
- **Analysis Dashboard**: View results after upload

## 📁 Project Structure
```
ElectroVision AI/
├── backend/          ← API Server (Port 3000)
│   ├── app.js        ← Main server file
│   ├── routes/       ← API routes
│   └── uploads/      ← Uploaded files
├── frontend/         ← React App (Port 3001)  
│   ├── src/          ← React components
│   └── public/       ← Static files
└── ai_model/         ← AI training scripts
```

## 🎯 Expected Workflow

1. **Start Backend**: `cd backend && npm start`
2. **Start Frontend**: `cd frontend && npm start`  
3. **Open Browser**: http://localhost:3001
4. **Upload File**: Drag & drop electrical plan
5. **View Results**: AI analysis appears on dashboard

## ⚡ Quick Test

After starting both servers:

1. **Open**: http://localhost:3001
2. **Upload**: Any PDF/DWG/DXF file
3. **Check**: Should process without "Upload failed" error
4. **Success**: File uploads and analysis runs

---

💡 **Tip**: Keep both terminal windows open to see server logs and debug any issues! 