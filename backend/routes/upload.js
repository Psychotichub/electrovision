const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Upload directory for immediate analysis
const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(__dirname, '../uploads');

// Source files directory for training data integration
const SOURCE_FILES_DIR = path.join(__dirname, '../../ai_model/source_files');

// Ensure upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Ensure source files directories exist
const sourceSubDirs = ['pdf', 'dwg', 'dxf', 'images'];
sourceSubDirs.forEach(subDir => {
  const dirPath = path.join(SOURCE_FILES_DIR, subDir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
});

const { analyzePlan } = require('../controllers/analyzeController');

const router = express.Router();

// Helper function to determine file type and appropriate source directory
const getSourceDirectory = (filename) => {
  const ext = path.extname(filename).toLowerCase();
  
  switch (ext) {
    case '.pdf':
      return path.join(SOURCE_FILES_DIR, 'pdf');
    case '.dwg':
      return path.join(SOURCE_FILES_DIR, 'dwg');
    case '.dxf':
      return path.join(SOURCE_FILES_DIR, 'dxf');
    case '.jpg':
    case '.jpeg':
    case '.png':
    case '.tiff':
    case '.tif':
    case '.bmp':
    case '.gif':
    case '.webp':
      return path.join(SOURCE_FILES_DIR, 'images');
    default:
      return null; // Unsupported file type
  }
};

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    // Create timestamp prefix for uploads directory
    const timestamp = Date.now();
    const filename = `${timestamp}-${file.originalname}`;
    cb(null, filename);
  }
});

const upload = multer({ 
  storage,
  fileFilter: (req, file, cb) => {
    // Check if file type is supported
    const ext = path.extname(file.originalname).toLowerCase();
    const supportedExtensions = ['.pdf', '.dwg', '.dxf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp'];
    
    if (supportedExtensions.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: ${ext}. Supported formats: PDF, DWG, DXF, JPG, PNG, TIFF, BMP, GIF, WEBP`));
    }
  },
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  }
});

router.post('/', upload.single('plan'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  
  console.log(`📤 File uploaded: ${req.file.filename} (${req.file.size} bytes)`);
  console.log(`📁 Upload path: ${req.file.path}`);
  
  try {
    // Copy file to appropriate source_files directory for training integration
    const sourceDir = getSourceDirectory(req.file.originalname);
    
    if (sourceDir) {
      // Use original filename (without timestamp) for source_files
      const sourceFilePath = path.join(sourceDir, req.file.originalname);
      
      // Check if file already exists in source directory
      let finalSourcePath = sourceFilePath;
      let counter = 1;
      
      while (fs.existsSync(finalSourcePath)) {
        const ext = path.extname(req.file.originalname);
        const baseName = path.basename(req.file.originalname, ext);
        finalSourcePath = path.join(sourceDir, `${baseName}_${counter}${ext}`);
        counter++;
      }
      
      // Copy file to source directory
      fs.copyFileSync(req.file.path, finalSourcePath);
      
      console.log(`📋 File copied to training source: ${finalSourcePath}`);
      console.log(`🎯 Ready for training data processing!`);
    } else {
      console.log(`⚠️  Unsupported file type for training: ${path.extname(req.file.originalname)}`);
    }
    
    // Perform analysis on the uploaded file
    const result = await analyzePlan(req.file.path);
    console.log('✅ Analysis completed successfully');
    
    // Enhanced response with file storage information
    res.json({ 
      status: 'success', 
      data: result,
      fileInfo: {
        originalName: req.file.originalname,
        uploadPath: req.file.path,
        sourcePath: sourceDir ? path.join(sourceDir, req.file.originalname) : null,
        addedToTraining: sourceDir !== null,
        message: sourceDir ? 
          '✅ File uploaded and added to training source files!' : 
          '✅ File uploaded and analyzed (not added to training - unsupported format)'
      }
    });
    
  } catch (error) {
    console.error('❌ Processing error:', error.message);
    console.error('📋 Full error:', error);
    
    // Return the specific error message
    res.status(500).json({ 
      error: error.message || 'Processing failed',
      timestamp: new Date().toISOString(),
      file: req.file.filename
    });
  }
});

module.exports = router;
