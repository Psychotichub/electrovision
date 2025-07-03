import sys
import json
import fitz  # PyMuPDF
import os
from PIL import Image
import numpy as np
import cv2
import io

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Optional OCR support - works without tesseract installed
try:
    import pytesseract
    # Test if tesseract executable is actually available
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        print("[SUCCESS] Tesseract OCR available - Enhanced text extraction enabled", file=sys.stderr)
    except Exception as e:
        TESSERACT_AVAILABLE = False
        print(f"[WARNING] Tesseract executable not found: {e}", file=sys.stderr)
        print("[INFO] PDF processing will use basic text extraction only", file=sys.stderr)
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[WARNING] pytesseract module not available - Using basic text extraction only", file=sys.stderr)

def extract_images_from_pdf(pdf_path, output_dir=None):
    """Extract images from PDF for AI analysis"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                img_data = pix.tobytes("png")
                
                if output_dir:
                    img_path = os.path.join(output_dir, f"page_{page_num}_img_{img_index}.png")
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    images.append(img_path)
                else:
                    images.append(img_data)
            
            pix = None
    
    doc.close()
    return images

def extract_text_with_ocr(pdf_path):
    """Extract text using OCR for scanned PDFs (if available)"""
    doc = fitz.open(pdf_path)
    all_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # First try regular text extraction
        text = page.get_text()
        if text.strip():
            all_text += f"\n--- Page {page_num + 1} ---\n{text}"
        else:
            # If no text found, try OCR if available
            if TESSERACT_AVAILABLE:
                try:
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    # Convert to PIL Image for OCR
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Try different Tesseract configurations for better compatibility
                    try:
                        # First try default
                        ocr_text = pytesseract.image_to_string(image)
                    except Exception as e1:
                        try:
                            # Try with specific config
                            ocr_text = pytesseract.image_to_string(image, config='--psm 6')
                        except Exception as e2:
                            raise Exception(f"Tesseract failed with multiple configs: {e1}, {e2}")
                    
                    all_text += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}"
                except Exception as ocr_error:
                    all_text += f"\n--- Page {page_num + 1} (OCR Failed) ---\n[Could not extract text: {ocr_error}]"
            else:
                all_text += f"\n--- Page {page_num + 1} (No Text) ---\n[Page contains images but OCR not available]"
    
    doc.close()
    return all_text

def detect_electrical_components(text):
    """Basic electrical component detection from text"""
    electrical_keywords = {
        'switch': ['switch', 'sw', 'interruptor'],
        'outlet': ['outlet', 'socket', 'receptacle', 'plug'],
        'light': ['light', 'lamp', 'fixture', 'luminaire'],
        'breaker': ['breaker', 'circuit breaker', 'cb'],
        'panel': ['panel', 'electrical panel', 'distribution panel'],
        'wire': ['wire', 'cable', 'conductor'],
        'ground': ['ground', 'earth', 'gnd'],
        'voltage': ['220v', '110v', '240v', '120v', 'volt'],
        'amperage': ['amp', 'ampere', 'a'],
        'power': ['kw', 'kilowatt', 'watt', 'w']
    }
    
    detected_components = []
    text_lower = text.lower()
    
    for component_type, keywords in electrical_keywords.items():
        count = 0
        positions = []
        
        for keyword in keywords:
            if keyword in text_lower:
                count += text_lower.count(keyword)
                # Find positions of keywords
                start = 0
                while True:
                    pos = text_lower.find(keyword, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
        
        if count > 0:
            detected_components.append({
                'type': component_type,
                'count': count,
                'positions': positions[:10]  # Limit to first 10 positions
            })
    
    return detected_components

def parse_pdf(file_path):
    """Main PDF parsing function"""
    try:
        # Create output directory for images
        output_dir = os.path.join(os.path.dirname(file_path), 'extracted_images')
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract text content
        text_content = extract_text_with_ocr(file_path)
        
        # Extract images for further AI analysis
        extracted_images = extract_images_from_pdf(file_path, output_dir)
        
        # Detect electrical components from text
        components = detect_electrical_components(text_content)
        
        # Get basic PDF info
        doc = fitz.open(file_path)
        pdf_info = {
            'pages': len(doc),
            'metadata': doc.metadata,
            'is_encrypted': doc.is_encrypted
        }
        doc.close()
        
        # Determine processing status
        if TESSERACT_AVAILABLE:
            status_message = 'PDF processed successfully with OCR support'
        else:
            status_message = 'PDF processed successfully (basic text extraction only - install Tesseract for enhanced OCR)'
        
        return {
            'text_content': text_content,
            'extracted_images': extracted_images,
            'detected_components': components,
            'pdf_info': pdf_info,
            'analysis_type': 'pdf_electrical_plan',
            'ocr_available': TESSERACT_AVAILABLE,
            'message': status_message,
            'ocr_note': 'For enhanced OCR support, install Tesseract: see INSTALL_TESSERACT.md' if not TESSERACT_AVAILABLE else None
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages for common issues
        if "tesseract" in error_msg.lower():
            error_msg = ("Tesseract OCR not found. For enhanced text extraction from scanned PDFs:\n" +
                        "• Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n" +
                        "• Add to PATH or install via: choco install tesseract\n" +
                        "• Basic PDF processing will continue without OCR")
        
        return {
            'error': f"PDF parsing failed: {error_msg}",
            'text_content': "",
            'extracted_images': [],
            'detected_components': [],
            'pdf_info': {},
            'ocr_available': TESSERACT_AVAILABLE
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'File path required'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    data = parse_pdf(file_path)
    print(json.dumps(data, indent=2))
