#!/usr/bin/env python3
"""
ElectroVision AI - Format Converter
Converts DWG/DXF files to images and handles annotation format conversions
"""

import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path
import argparse
import logging
from tqdm import tqdm
import subprocess
import shutil
import ezdxf
from ezdxf.addons.drawing import matplotlib, RenderContext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormatConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.setup_directories()
        
    def setup_directories(self):
        """Create output directory structure"""
        directories = [
            'images/dxf_converted',
            'images/dwg_converted', 
            'images/processed',
            'annotations/yolo',
            'annotations/coco',
            'annotations/voc',
            'metadata',
            'dataset/train/images',
            'dataset/train/labels',
            'dataset/val/images',
            'dataset/val/labels'
        ]
        
        for dir_name in directories:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Created output directory structure in {self.output_dir}")

    def convert_dwg_to_dxf(self, dwg_path):
        """Convert DWG to DXF using ODA File Converter or dwg2dxf"""
        dwg_path = Path(dwg_path)
        dxf_path = self.output_dir / 'temp' / f'{dwg_path.stem}.dxf'
        dxf_path.parent.mkdir(exist_ok=True)
        
        try:
            # Try using ODA File Converter (if available)
            cmd = [
                'ODAFileConverter', 
                str(dwg_path.parent), 
                str(dxf_path.parent),
                'ACAD2018', 'DXF', '0', '1', 
                f'{dwg_path.name}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and dxf_path.exists():
                logger.info(f"Successfully converted {dwg_path.name} to DXF")
                return dxf_path
            else:
                logger.warning(f"ODA File Converter failed for {dwg_path.name}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ODA File Converter not available or timed out")
        
        # Alternative: try using dwg2dxf (if available)
        try:
            cmd = ['dwg2dxf', '-o', str(dxf_path), str(dwg_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and dxf_path.exists():
                logger.info(f"Successfully converted {dwg_path.name} to DXF using dwg2dxf")
                return dxf_path
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("dwg2dxf not available")
        
        logger.error(f"Could not convert {dwg_path.name} to DXF")
        return None

    def convert_dxf_to_image(self, dxf_path, output_type='dxf'):
        """Convert DXF file to high-quality image"""
        dxf_path = Path(dxf_path)
        
        try:
            # Read DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            
            # Create matplotlib figure
            fig = plt.figure(figsize=(20, 16), dpi=150)
            ax = fig.add_subplot(111)
            
            # Create render context
            ctx = RenderContext(doc)
            
            # Render to matplotlib
            out = matplotlib.MatplotlibBackend(ax)
            matplotlib.Frontend(ctx, out).draw_layout(msp, finalize=True)
            
            # Set background to white
            ax.set_facecolor('white')
            fig.patch.set_facecolor('white')
            
            # Remove axes for cleaner image
            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis('off')
            
            # Save high-quality image
            if output_type == 'dwg':
                img_path = self.output_dir / 'images/dwg_converted' / f'{dxf_path.stem}.png'
            else:
                img_path = self.output_dir / 'images/dxf_converted' / f'{dxf_path.stem}.png'
            
            plt.savefig(img_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"Successfully converted {dxf_path.name} to image")
            
            # Post-process image for better AI training
            processed_path = self.post_process_cad_image(img_path)
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Error converting {dxf_path.name} to image: {e}")
            return None

    def post_process_cad_image(self, img_path):
        """Post-process CAD image for better AI training"""
        img_path = Path(img_path)
        processed_path = self.output_dir / 'images/processed' / img_path.name
        
        try:
            # Load image
            img = cv2.imread(str(img_path))
            if img is None:
                return None
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(filtered)
            
            # Apply morphological operations to clean up lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            cleaned = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to BGR for consistency
            final_img = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
            
            # Save processed image
            cv2.imwrite(str(processed_path), final_img)
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Error post-processing {img_path}: {e}")
            return None

    def convert_coco_to_yolo(self, coco_json_path, images_dir):
        """Convert COCO format annotations to YOLO format"""
        coco_json_path = Path(coco_json_path)
        images_dir = Path(images_dir)
        
        try:
            with open(coco_json_path, 'r') as f:
                coco_data = json.load(f)
            
            # Create category mapping
            categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
            
            # Group annotations by image
            image_annotations = {}
            for ann in coco_data['annotations']:
                img_id = ann['image_id']
                if img_id not in image_annotations:
                    image_annotations[img_id] = []
                image_annotations[img_id].append(ann)
            
            # Convert each image's annotations
            for img_info in coco_data['images']:
                img_id = img_info['id']
                img_width = img_info['width']
                img_height = img_info['height']
                img_filename = img_info['file_name']
                
                # Create YOLO label file
                yolo_filename = Path(img_filename).stem + '.txt'
                yolo_path = self.output_dir / 'annotations/yolo' / yolo_filename
                
                yolo_annotations = []
                
                if img_id in image_annotations:
                    for ann in image_annotations[img_id]:
                        # Convert COCO bbox to YOLO format
                        x, y, w, h = ann['bbox']
                        
                        # Normalize coordinates
                        x_center = (x + w/2) / img_width
                        y_center = (y + h/2) / img_height
                        norm_width = w / img_width
                        norm_height = h / img_height
                        
                        # Get class ID (assuming categories are mapped to indices)
                        class_name = categories[ann['category_id']]
                        class_id = self.get_class_id(class_name)
                        
                        yolo_annotations.append(
                            f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}"
                        )
                
                # Write YOLO annotation file
                with open(yolo_path, 'w') as f:
                    f.write('\n'.join(yolo_annotations))
            
            logger.info(f"Successfully converted COCO annotations to YOLO format")
            
        except Exception as e:
            logger.error(f"Error converting COCO to YOLO: {e}")

    def convert_voc_to_yolo(self, voc_dir):
        """Convert Pascal VOC format annotations to YOLO format"""
        voc_dir = Path(voc_dir)
        annotations_dir = voc_dir / 'Annotations'
        
        if not annotations_dir.exists():
            logger.error(f"VOC annotations directory not found: {annotations_dir}")
            return
        
        try:
            for xml_file in annotations_dir.glob('*.xml'):
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Get image dimensions
                size = root.find('size')
                img_width = int(size.find('width').text)
                img_height = int(size.find('height').text)
                
                yolo_annotations = []
                
                # Process each object
                for obj in root.findall('object'):
                    class_name = obj.find('name').text
                    class_id = self.get_class_id(class_name)
                    
                    bbox = obj.find('bndbox')
                    xmin = int(bbox.find('xmin').text)
                    ymin = int(bbox.find('ymin').text)
                    xmax = int(bbox.find('xmax').text)
                    ymax = int(bbox.find('ymax').text)
                    
                    # Convert to YOLO format
                    x_center = (xmin + xmax) / 2.0 / img_width
                    y_center = (ymin + ymax) / 2.0 / img_height
                    width = (xmax - xmin) / img_width
                    height = (ymax - ymin) / img_height
                    
                    yolo_annotations.append(
                        f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                    )
                
                # Write YOLO annotation file
                yolo_filename = xml_file.stem + '.txt'
                yolo_path = self.output_dir / 'annotations/yolo' / yolo_filename
                
                with open(yolo_path, 'w') as f:
                    f.write('\n'.join(yolo_annotations))
            
            logger.info("Successfully converted VOC annotations to YOLO format")
            
        except Exception as e:
            logger.error(f"Error converting VOC to YOLO: {e}")

    def get_class_id(self, class_name):
        """Map class name to ID for YOLO format"""
        class_mapping = {
            'switch': 0,
            'outlet': 1, 
            'light': 2,
            'panel': 3,
            'wire': 4,
            'junction': 5,
            'breaker': 6,
            'ground': 7,
            'measurement': 8,
            'motor': 9,
            'transformer': 10,
            'sensor': 11
        }
        
        return class_mapping.get(class_name.lower(), 0)

    def process_cad_files(self):
        """Process all CAD files in the input directory"""
        # Find DXF files
        dxf_files = list(self.input_dir.glob('*.dxf'))
        dwg_files = list(self.input_dir.glob('*.dwg'))
        
        logger.info(f"Found {len(dxf_files)} DXF files and {len(dwg_files)} DWG files")
        
        processed_images = []
        
        # Process DXF files directly
        for dxf_file in tqdm(dxf_files, desc="Processing DXF files"):
            img_path = self.convert_dxf_to_image(dxf_file, 'dxf')
            if img_path:
                processed_images.append(img_path)
        
        # Convert DWG to DXF then to image
        for dwg_file in tqdm(dwg_files, desc="Processing DWG files"):
            dxf_path = self.convert_dwg_to_dxf(dwg_file)
            if dxf_path:
                img_path = self.convert_dxf_to_image(dxf_path, 'dwg')
                if img_path:
                    processed_images.append(img_path)
                # Clean up temporary DXF
                dxf_path.unlink(missing_ok=True)
        
        # Prepare training dataset
        self.prepare_training_dataset(processed_images)
        
        logger.info(f"CAD file processing completed! Processed {len(processed_images)} images")

    def prepare_training_dataset(self, processed_images, train_split=0.8):
        """Prepare dataset for YOLO training"""
        if not processed_images:
            logger.warning("No processed images to prepare for training")
            return
        
        logger.info("Preparing training dataset...")
        
        # Split into train and validation
        np.random.shuffle(processed_images)
        split_idx = int(len(processed_images) * train_split)
        
        train_images = processed_images[:split_idx]
        val_images = processed_images[split_idx:]
        
        # Copy to dataset directories
        for img_path in train_images:
            img_path = Path(img_path)
            dest_path = self.output_dir / 'dataset/train/images' / img_path.name
            shutil.copy2(img_path, dest_path)
            
            # Create empty label file
            label_path = self.output_dir / 'dataset/train/labels' / f'{img_path.stem}.txt'
            label_path.touch()
        
        for img_path in val_images:
            img_path = Path(img_path)
            dest_path = self.output_dir / 'dataset/val/images' / img_path.name
            shutil.copy2(img_path, dest_path)
            
            # Create empty label file
            label_path = self.output_dir / 'dataset/val/labels' / f'{img_path.stem}.txt'
            label_path.touch()
        
        logger.info(f"Dataset prepared: {len(train_images)} training, {len(val_images)} validation images")

def main():
    parser = argparse.ArgumentParser(description='Convert CAD files and annotation formats')
    parser.add_argument('input_dir', help='Directory containing CAD files')
    parser.add_argument('output_dir', help='Output directory for converted files')
    parser.add_argument('--format', choices=['cad', 'coco', 'voc'], default='cad',
                       help='Conversion type (default: cad)')
    parser.add_argument('--train-split', type=float, default=0.8,
                       help='Train/validation split ratio (default: 0.8)')
    
    args = parser.parse_args()
    
    converter = FormatConverter(args.input_dir, args.output_dir)
    
    if args.format == 'cad':
        converter.process_cad_files()
    elif args.format == 'coco':
        coco_json = input("Enter path to COCO JSON file: ")
        images_dir = input("Enter path to images directory: ")
        converter.convert_coco_to_yolo(coco_json, images_dir)
    elif args.format == 'voc':
        converter.convert_voc_to_yolo(args.input_dir)

if __name__ == "__main__":
    # For direct execution with default paths
    if len(sys.argv) == 1:
        input_dir = input("Enter input directory path (containing CAD files): ")
        output_dir = input("Enter output directory path: ")
        
        if not input_dir or not output_dir:
            print("Using default paths...")
            input_dir = "../backend/uploads"
            output_dir = "converted_data"
        
        converter = FormatConverter(input_dir, output_dir)
        converter.process_cad_files()
    else:
        main()
