# 🔧 Install Tesseract OCR for Enhanced PDF Processing

## 🎯 What is Tesseract?

Tesseract OCR enables **text extraction from scanned PDFs** and image-based electrical plans. Without it, you can still process PDF files, but only text-based (not scanned) content will be extracted.

## ⚡ Quick Install (Windows)

### Option 1: Download Installer (Recommended)
1. **Download**: https://github.com/UB-Mannheim/tesseract/wiki
2. **Run**: `tesseract-ocr-w64-setup-5.x.x.exe`
3. **Install** with default settings
4. **Restart** your terminal/command prompt

### Option 2: Using Chocolatey
```bash
# Install Chocolatey first (if not installed)
# Then run:
choco install tesseract
```

### Option 3: Using Scoop
```bash
scoop install tesseract
```

## 🔍 Verify Installation

Test if Tesseract is properly installed:
```bash
tesseract --version
# Should show: tesseract 5.x.x
```

## 📊 Before vs After

### ❌ Without Tesseract:
```json
{
  "status": "success", 
  "data": {
    "error": "tesseract is not installed...",
    "text_content": "",
    "detected_components": []
  }
}
```

### ✅ With Tesseract:
```json
{
  "status": "success",
  "data": {
    "text_content": "Electrical Plan - Kitchen Layout\n120V outlets, LED lights...",
    "detected_components": [
      {"type": "outlet", "count": 8},
      {"type": "light", "count": 12},
      {"type": "switch", "count": 6}
    ],
    "ocr_available": true,
    "message": "PDF processed successfully with OCR support"
  }
}
```

## 🚀 Test Your Installation

1. **Upload a PDF** with scanned electrical plans
2. **Check the response** - should now show extracted text
3. **Look for**: `"ocr_available": true` in the response

## 🛠️ Troubleshooting

### "tesseract command not found"
- **Solution**: Add Tesseract to your PATH
- **Path**: Usually `C:\Program Files\Tesseract-OCR`
- **Add to PATH**: System Properties → Environment Variables → Add to PATH

### "Permission denied"
- **Solution**: Run command prompt as Administrator
- **Or**: Install to user directory instead of Program Files

### Still not working?
1. **Restart terminal** after installation
2. **Check PATH**: `echo $env:PATH` (PowerShell) or `echo %PATH%` (CMD)
3. **Manual path**: Look for `tesseract.exe` in Program Files

## 📁 Alternative: Manual PATH Setup

If automatic PATH doesn't work:

1. **Find Tesseract**: Usually `C:\Program Files\Tesseract-OCR\tesseract.exe`
2. **Add to PATH**:
   - Windows Key + R → `sysdm.cpl`
   - Advanced → Environment Variables
   - System Variables → PATH → Edit → New
   - Add: `C:\Program Files\Tesseract-OCR`
   - OK → OK → OK
3. **Restart terminal**

## 🎯 Benefits of OCR

With Tesseract installed, your system can:
- ✅ **Extract text** from scanned electrical plans
- ✅ **Detect components** in image-based PDFs  
- ✅ **Process CAD exports** that were saved as images
- ✅ **Handle mixed content** (text + images in same PDF)

## 💡 Pro Tips

- **Quality matters**: Higher resolution PDFs = better OCR results
- **Clean scans**: Remove noise/artifacts for better text recognition
- **Language packs**: Tesseract supports multiple languages if needed
- **Batch processing**: OCR works on multiple pages automatically

---

🚀 **After installation, restart your backend server and try uploading PDFs again!**

```bash
# Restart backend with OCR support
cd backend
npm start
``` 