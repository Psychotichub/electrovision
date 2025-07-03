#!/usr/bin/env python3
"""
ElectroVision AI - PDF Data Extraction
Comprehensive script for extracting images and text from electrical plan PDFs
"""

import os
import sys
import json
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from pathlib import Path
import argparse
import logging
from tqdm import tqdm
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFDataExtractor:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.setup_directories()
        
    def setup_directories(self):
        """Create output directory structure"""
        directories = [
            'images/raw',
            'images/processed', 
            'images/annotated',
            'text/raw',
            'text/processed',
            'metadata',
            'dataset/train/images',
            'dataset/train/labels',
            'dataset/val/images', 
            'dataset/val/labels'
        ]
        
        for dir_name in directories:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Created output directory structure in {self.output_dir}")

    def extract_pdf_data(self, pdf_path):
        """Extract all data from a single PDF"""
        pdf_path = Path(pdf_path)
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        try:
            doc = fitz.open(pdf_path)
            pdf_data = {
                'filename': pdf_path.name,
                'pages': len(doc),
                'metadata': doc.metadata,
                'extracted_images': [],
                'text_content': {},
                'electrical_components': []
            }
            
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                
                page = doc.load_page(page_num)
                
                # Extract images
                page_images = self.extract_images_from_page(page, page_num, pdf_path.stem)
                pdf_data['extracted_images'].extend(page_images)
                
                # Extract text
                page_text = self.extract_text_from_page(page, page_num)
                pdf_data['text_content'][f'page_{page_num + 1}'] = page_text
                
                # Detect electrical components in text
                components = self.detect_electrical_keywords(page_text)
                if components:
                    pdf_data['electrical_components'].extend([
                        {**comp, 'page': page_num + 1} for comp in components
                    ])
            
            doc.close()
            
            # Save metadata
            metadata_file = self.output_dir / 'metadata' / f'{pdf_path.stem}.json'
            with open(metadata_file, 'w') as f:
                json.dump(pdf_data, f, indent=2)
                
            return pdf_data
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return None

    def extract_images_from_page(self, page, page_num, pdf_stem):
        """Extract and process images from a PDF page"""
        extracted_images = []
        
        # Method 1: Extract embedded images
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    
                    # Save raw image
                    img_filename = f'{pdf_stem}_p{page_num+1}_img{img_index}.png'
                    raw_img_path = self.output_dir / 'images/raw' / img_filename
                    
                    with open(raw_img_path, 'wb') as f:
                        f.write(img_data)
                    
                    # Process image for better AI training
                    processed_img_path = self.process_image_for_training(raw_img_path)
                    
                    extracted_images.append({
                        'filename': img_filename,
                        'raw_path': str(raw_img_path),
                        'processed_path': str(processed_img_path),
                        'page': page_num + 1,
                        'type': 'embedded'
                    })
                
                pix = None
                
            except Exception as e:
                logger.warning(f"Could not extract image {img_index} from page {page_num + 1}: {e}")
        
        # Method 2: Render entire page as image (for scanned PDFs)
        page_pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        page_img_data = page_pix.tobytes("png")
        
        page_img_filename = f'{pdf_stem}_page_{page_num+1}_full.png'
        page_img_path = self.output_dir / 'images/raw' / page_img_filename
        
        with open(page_img_path, 'wb') as f:
            f.write(page_img_data)
        
        # Process full page image
        processed_page_path = self.process_image_for_training(page_img_path)
        
        extracted_images.append({
            'filename': page_img_filename,
            'raw_path': str(page_img_path),
            'processed_path': str(processed_page_path),
            'page': page_num + 1,
            'type': 'full_page'
        })
        
        page_pix = None
        
        return extracted_images

    def extract_text_from_page(self, page, page_num):
        """Extract text from page using multiple methods"""
        text_data = {
            'raw_text': '',
            'ocr_text': '',
            'combined_text': ''
        }
        
        # Method 1: Direct text extraction
        raw_text = page.get_text()
        text_data['raw_text'] = raw_text.strip()
        
        # Method 2: OCR if no text found or text is sparse
        if len(raw_text.strip()) < 50:  # Likely scanned document
            try:
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Enhance image for better OCR
                enhanced_img = self.enhance_image_for_ocr(img)
                
                ocr_text = pytesseract.image_to_string(enhanced_img)
                text_data['ocr_text'] = ocr_text.strip()
                
                pix = None
                
            except Exception as e:
                logger.warning(f"OCR failed for page {page_num + 1}: {e}")
                text_data['ocr_text'] = ""
        
        # Combine texts
        text_data['combined_text'] = f"{text_data['raw_text']}\n{text_data['ocr_text']}".strip()
        
        return text_data

    def enhance_image_for_ocr(self, image):
        """Enhance image quality for better OCR results"""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image

    def process_image_for_training(self, image_path):
        """Process image for AI training dataset"""
        image_path = Path(image_path)
        processed_path = self.output_dir / 'images/processed' / image_path.name
        
        try:
            # Load image
            img = cv2.imread(str(image_path))
            if img is None:
                logger.warning(f"Could not load image: {image_path}")
                return None
            
            # Preprocessing pipeline
            processed_img = self.preprocessing_pipeline(img)
            
            # Save processed image
            cv2.imwrite(str(processed_path), processed_img)
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None

    def preprocessing_pipeline(self, img):
        """Image preprocessing pipeline for electrical drawings"""
        # Convert to LAB color space for better enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge and convert back
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        # Sharpen the image
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened

    def detect_electrical_keywords(self, text_data):
        """Detect electrical components mentioned in text"""
        electrical_patterns = {
            'switch': [
                r'\bswitch\b', r'\bsw\b', r'\btoggle\b', r'\binterruptor\b'
            ],
            'outlet': [
                r'\boutlet\b', r'\bsocket\b', r'\breceptacle\b', r'\bplug\b'
            ],
            'light': [
                r'\blight\b', r'\blamp\b', r'\bfixture\b', r'\bluminaire\b',
                r'\bceiling\s+light\b', r'\brecessed\b'
            ],
            'panel': [
                r'\bpanel\b', r'\belectrical\s+panel\b', r'\bdistribution\b',
                r'\bbreaker\s+panel\b', r'\bmain\s+panel\b'
            ],
            'wire': [
                r'\bwire\b', r'\bcable\b', r'\bconductor\b', r'\bconduit\b'
            ],
            'voltage': [
                r'\b\d+\s*v\b', r'\b\d+\s*volt\b', r'\b110v\b', r'\b220v\b', r'\b240v\b'
            ],
            'amperage': [
                r'\b\d+\s*a\b', r'\b\d+\s*amp\b', r'\bampere\b'
            ],
            'power': [
                r'\b\d+\s*w\b', r'\b\d+\s*watt\b', r'\bkw\b', r'\bkilowatt\b'
            ]
        }
        
        combined_text = text_data.get('combined_text', '').lower()
        detected_components = []
        
        for component_type, patterns in electrical_patterns.items():
            for pattern in patterns:
                import re
                matches = re.finditer(pattern, combined_text, re.IGNORECASE)
                for match in matches:
                    detected_components.append({
                        'type': component_type,
                        'text': match.group(),
                        'position': match.span(),
                        'confidence': 0.8  # Basic confidence score
                    })
        
        return detected_components

    def prepare_training_dataset(self, train_split=0.8):
        """Prepare dataset for YOLO training"""
        logger.info("Preparing training dataset...")
        
        processed_images = list((self.output_dir / 'images/processed').glob('*.png'))
        
        if not processed_images:
            logger.warning("No processed images found for dataset preparation")
            return
        
        # Split into train and validation
        np.random.shuffle(processed_images)
        split_idx = int(len(processed_images) * train_split)
        
        train_images = processed_images[:split_idx]
        val_images = processed_images[split_idx:]
        
        # Copy to dataset directories
        for img_path in train_images:
            dest_path = self.output_dir / 'dataset/train/images' / img_path.name
            shutil.copy2(img_path, dest_path)
            
            # Create empty label file
            label_path = self.output_dir / 'dataset/train/labels' / f'{img_path.stem}.txt'
            label_path.touch()
        
        for img_path in val_images:
            dest_path = self.output_dir / 'dataset/val/images' / img_path.name
            shutil.copy2(img_path, dest_path)
            
            # Create empty label file
            label_path = self.output_dir / 'dataset/val/labels' / f'{img_path.stem}.txt'
            label_path.touch()
        
        logger.info(f"Dataset prepared: {len(train_images)} training, {len(val_images)} validation images")

    def process_directory(self):
        """Process all PDFs in the input directory"""
        pdf_files = list(self.input_dir.glob('*.pdf'))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.input_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            self.extract_pdf_data(pdf_file)
        
        # Prepare training dataset
        self.prepare_training_dataset()
        
        logger.info("PDF processing completed!")

def main():
    parser = argparse.ArgumentParser(description='Extract data from electrical plan PDFs')
    parser.add_argument('input_dir', help='Directory containing PDF files')
    parser.add_argument('output_dir', help='Output directory for extracted data')
    parser.add_argument('--train-split', type=float, default=0.8, 
                       help='Train/validation split ratio (default: 0.8)')
    
    args = parser.parse_args()
    
    extractor = PDFDataExtractor(args.input_dir, args.output_dir)
    extractor.process_directory()

if __name__ == "__main__":
    # For direct execution with default paths
    if len(sys.argv) == 1:
        input_dir = input("Enter input directory path (containing PDFs): ")
        output_dir = input("Enter output directory path: ")
        
        if not input_dir or not output_dir:
            print("Using default paths...")
            input_dir = "../backend/uploads"
            output_dir = "extracted_data"
        
        extractor = PDFDataExtractor(input_dir, output_dir)
        extractor.process_directory()
    else:
        main()
