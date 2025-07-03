const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const PYTHON_CMD = process.env.PYTHON_CMD || 'python';

function analyzePlan(filePath) {
  return new Promise((resolve, reject) => {
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return reject(new Error(`File not found: ${filePath}`));
    }

    // Get file extension
    const ext = path.extname(filePath).toLowerCase();
    console.log(`🔍 Analyzing file: ${filePath} (${ext})`);

    // Determine script based on file extension
    let scriptPath = '';
    if (ext === '.pdf') {
      scriptPath = 'python/parse_pdf.py';
    } else if (ext === '.dxf') {
      scriptPath = 'python/parse_dxf.py';
    } else if (ext === '.dwg') {
      // DWG files need special handling - they should be converted to DXF first
      // For now, try DXF parser but inform user about conversion need
      scriptPath = 'python/parse_dxf.py';
      console.log('⚠️ DWG file detected - may need conversion to DXF for proper parsing');
    } else {
      return reject(new Error(`Unsupported file format: ${ext}. Supported formats: .pdf, .dxf, .dwg`));
    }

    // Check if script exists
    const fullScriptPath = path.join(__dirname, '..', scriptPath);
    if (!fs.existsSync(fullScriptPath)) {
      return reject(new Error(`Analysis script not found: ${fullScriptPath}`));
    }

    console.log(`📄 Using script: ${scriptPath}`);
    console.log(`🐍 Python command: ${PYTHON_CMD}`);

    // Execute the Python script with UTF-8 encoding
    execFile(PYTHON_CMD, [scriptPath, filePath], { 
      cwd: path.join(__dirname, '..'),
      timeout: 30000, // 30 second timeout
      env: { 
        ...process.env, 
        PYTHONIOENCODING: 'utf-8',
        PYTHONLEGACYWINDOWSSTDIO: '1'
      }
    }, (error, stdout, stderr) => {
      
      if (error) {
        console.error('❌ Python execution error:', error.message);
        console.error('📋 stderr:', stderr);
        
        // Provide more specific error messages
        if (error.code === 'ENOENT') {
          return reject(new Error(`Python not found. Please ensure Python is installed and accessible as '${PYTHON_CMD}'`));
        }
        
        if (stderr.includes('ModuleNotFoundError')) {
          const moduleName = stderr.match(/No module named '(\w+)'/)?.[1] || 'unknown';
          return reject(new Error(`Missing Python dependency: ${moduleName}. Please install it with: pip install ${moduleName}`));
        }
        
        if (stderr.includes('FileDataError') || stderr.includes('cannot find document handler')) {
          return reject(new Error(`Invalid file format. The uploaded file may be corrupted or not a valid ${ext.slice(1).toUpperCase()} file.`));
        }
        
        return reject(new Error(`Analysis failed: ${error.message}${stderr ? ` - ${stderr}` : ''}`));
      }

      // Parse JSON output
      try {
        console.log('✅ Raw Python output:', stdout);
        const data = JSON.parse(stdout);
        console.log('📊 Parsed analysis data:', data);
        resolve(data);
      } catch (parseError) {
        console.error('❌ JSON parse error:', parseError.message);
        console.error('📋 Raw output:', stdout);
        reject(new Error(`Failed to parse analysis results. Raw output: ${stdout}`));
      }
    });
  });
}

module.exports = { analyzePlan };
