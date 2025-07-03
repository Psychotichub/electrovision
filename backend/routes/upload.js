const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(__dirname, '../uploads');

if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}
const { analyzePlan } = require('../controllers/analyzeController');

const router = express.Router();

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage });

router.post('/', upload.single('plan'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  
  console.log(`📤 File uploaded: ${req.file.filename} (${req.file.size} bytes)`);
  console.log(`📁 File path: ${req.file.path}`);
  
  try {
    const result = await analyzePlan(req.file.path);
    console.log('✅ Analysis completed successfully');
    res.json({ status: 'success', data: result });
  } catch (error) {
    console.error('❌ Analysis error:', error.message);
    console.error('📋 Full error:', error);
    
    // Return the specific error message instead of generic "Analysis failed"
    res.status(500).json({ 
      error: error.message || 'Analysis failed',
      timestamp: new Date().toISOString(),
      file: req.file.filename
    });
  }
});

module.exports = router;
