#!/usr/bin/env python3
"""
⚡ ElectroVision AI - DWG/PDF/Image to Training Data Converter

This script converts your DWG, PDF, and image electrical plans into training images
that can be annotated and used for AI model training.

Supported formats:
• PDF files (multi-page extraction)
• DWG files (converted via DXF)
• DXF files (vector to raster conversion)
• Image files (JPG, PNG, TIFF, BMP, GIF, WEBP)
"""

import os
import sys
import fitz  # PyMuPDF
import ezdxf
from pathlib import Path
from PIL import Image, ImageEnhance
import argparse
import shutil
from typing import List, Tuple
import subprocess

def setup_directories():
    """Create necessary directories for training data"""
    dirs = [
        "dataset/images/train",
        "dataset/images/val", 
        "dataset/labels/train",
        "dataset/labels/val",
        "source_files/pdf",
        "source_files/dwg", 
        "source_files/dxf",
        "source_files/images",
        "extracted_images"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created directory structure")

def pdf_to_images(pdf_path: str, output_dir: str, prefix: str = "plan") -> List[str]:
    """Extract images from PDF electrical plans"""
    
    print(f"📄 Processing PDF: {pdf_path}")
    
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_files = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Convert to image with high DPI for better quality
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom = ~300 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Save as PNG first for quality
            png_filename = f"{output_dir}/{prefix}_page_{page_num+1:03d}.png"
            pix.save(png_filename)
            
            # Convert to JPG for training (smaller file size)
            img = Image.open(png_filename)
            
            # Enhance image quality for better AI training
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)  # Slight contrast boost
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            jpg_filename = f"{output_dir}/{prefix}_page_{page_num+1:03d}.jpg"
            img.save(jpg_filename, 'JPEG', quality=95)
            
            # Remove PNG file to save space
            os.remove(png_filename)
            
            extracted_files.append(jpg_filename)
            print(f"  ✅ Extracted page {page_num+1} → {jpg_filename}")
        
        pdf_document.close()
        return extracted_files
        
    except Exception as e:
        print(f"  ❌ Error processing PDF: {e}")
        return []

def dwg_to_dxf(dwg_path: str, output_dir: str) -> str:
    """Convert DWG to DXF using AutoCAD or LibreCAD if available"""
    
    print(f"📐 Converting DWG: {dwg_path}")
    
    # Try different conversion methods
    dwg_file = Path(dwg_path)
    dxf_filename = f"{output_dir}/{dwg_file.stem}.dxf"
    
    # Method 1: Try using ezdxf (limited DWG support)
    try:
        doc = ezdxf.readfile(dwg_path)
        doc.saveas(dxf_filename)
        print(f"  ✅ Converted using ezdxf → {dxf_filename}")
        return dxf_filename
    except:
        pass
    
    # Method 2: Try ODA File Converter (if installed)
    try:
        result = subprocess.run([
            'ODAFileConverter', dwg_path, output_dir, 
            'ACAD2018', 'DXF', '0', '1', dxf_filename
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(dxf_filename):
            print(f"  ✅ Converted using ODA File Converter → {dxf_filename}")
            return dxf_filename
    except:
        pass
    
    # Method 3: Copy as DXF and try to read (some DWG files are compatible)
    try:
        shutil.copy2(dwg_path, dxf_filename)
        doc = ezdxf.readfile(dxf_filename)  # Test if readable
        print(f"  ✅ DWG file is DXF-compatible → {dxf_filename}")
        return dxf_filename
    except:
        if os.path.exists(dxf_filename):
            os.remove(dxf_filename)
    
    print(f"  ⚠️ Could not convert DWG to DXF. Please use AutoCAD or LibreCAD to convert manually.")
    return None

def dxf_to_image(dxf_path: str, output_dir: str, prefix: str = "plan") -> List[str]:
    """Convert DXF file to image using matplotlib"""
    
    print(f"📋 Processing DXF: {dxf_path}")
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import Polygon
        
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # Set up the plot
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.set_aspect('equal')
        
        # Track bounds to set proper limits
        all_x, all_y = [], []
        
        # Process different entity types
        for entity in msp:
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                ax.plot([start.x, end.x], [start.y, end.y], 'k-', linewidth=0.5)
                all_x.extend([start.x, end.x])
                all_y.extend([start.y, end.y])
                
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                circle = plt.Circle((center.x, center.y), radius, fill=False, color='black', linewidth=0.5)
                ax.add_patch(circle)
                all_x.extend([center.x - radius, center.x + radius])
                all_y.extend([center.y - radius, center.y + radius])
                
            elif entity.dxftype() == 'ARC':
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                
                import numpy as np
                angles = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
                x_coords = center.x + radius * np.cos(angles)
                y_coords = center.y + radius * np.sin(angles)
                ax.plot(x_coords, y_coords, 'k-', linewidth=0.5)
                all_x.extend(x_coords)
                all_y.extend(y_coords)
                
            elif entity.dxftype() == 'LWPOLYLINE':
                points = list(entity.get_points())
                if len(points) > 1:
                    x_coords = [p[0] for p in points]
                    y_coords = [p[1] for p in points]
                    ax.plot(x_coords, y_coords, 'k-', linewidth=0.5)
                    all_x.extend(x_coords)
                    all_y.extend(y_coords)
                    
            elif entity.dxftype() == 'TEXT':
                text_pos = entity.dxf.insert
                text_content = entity.dxf.text
                ax.text(text_pos.x, text_pos.y, text_content, fontsize=8, color='black')
                all_x.append(text_pos.x)
                all_y.append(text_pos.y)
        
        # Set plot limits with some padding
        if all_x and all_y:
            margin_x = (max(all_x) - min(all_x)) * 0.1
            margin_y = (max(all_y) - min(all_y)) * 0.1
            ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
            ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)
        
        # Clean up the plot
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Save as high-quality image
        dxf_file = Path(dxf_path)
        image_filename = f"{output_dir}/{prefix}_{dxf_file.stem}.jpg"
        
        plt.savefig(image_filename, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', format='jpg')
        plt.close()
        
        print(f"  ✅ Converted to image → {image_filename}")
        return [image_filename]
        
    except Exception as e:
        print(f"  ❌ Error converting DXF to image: {e}")
        return []

def process_image_files(image_path: str, output_dir: str, prefix: str = "img") -> List[str]:
    """Process image files for training (JPG, PNG, TIFF, BMP, GIF, etc.)"""
    
    print(f"🖼️ Processing Image: {image_path}")
    
    try:
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if needed (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            # Handle transparency for RGBA images
            if img.mode == 'RGBA':
                # Create white background
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = rgb_img
            else:
                img = img.convert('RGB')
        
        # Enhance image quality for AI training
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # Slight contrast boost
        
        # Enhance sharpness for better feature detection
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)  # Slight sharpness boost
        
        # Optional: Resize very large images to reasonable size (max 4K width/height)
        max_size = 4096
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            print(f"  📏 Resized large image to {img.width}x{img.height}")
        
        # Save as high-quality JPG
        image_file = Path(image_path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist
        jpg_filename = f"{output_dir}/{prefix}_{image_file.stem}.jpg"
        img.save(jpg_filename, 'JPEG', quality=95)
        
        print(f"  ✅ Processed image → {jpg_filename}")
        return [jpg_filename]
        
    except Exception as e:
        print(f"  ❌ Error processing image: {e}")
        return []

def organize_training_data(image_files: List[str], split_ratio: float = 0.8):
    """Organize extracted images into train/val splits"""
    
    print(f"\n📁 Organizing {len(image_files)} images for training...")
    
    # Shuffle the list for random split
    import random
    random.shuffle(image_files)
    
    # Calculate split point
    split_point = int(len(image_files) * split_ratio)
    train_files = image_files[:split_point]
    val_files = image_files[split_point:]
    
    # Copy to training directories
    for i, img_file in enumerate(train_files):
        dest_file = f"dataset/images/train/train_img_{i+1:03d}.jpg"
        shutil.copy2(img_file, dest_file)
        
        # Create empty label file
        label_file = f"dataset/labels/train/train_img_{i+1:03d}.txt"
        Path(label_file).touch()
    
    for i, img_file in enumerate(val_files):
        dest_file = f"dataset/images/val/val_img_{i+1:03d}.jpg"
        shutil.copy2(img_file, dest_file)
        
        # Create empty label file
        label_file = f"dataset/labels/val/val_img_{i+1:03d}.txt"
        Path(label_file).touch()
    
    print(f"✅ Training set: {len(train_files)} images")
    print(f"✅ Validation set: {len(val_files)} images")
    
    return len(train_files), len(val_files)

def scan_source_files(source_dir: str) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Scan for PDF, DWG, DXF, and image files in source directory"""
    
    pdf_files = []
    dwg_files = []
    dxf_files = []
    image_files = []
    
    source_path = Path(source_dir)
    if source_path.exists():
        # PDF files
        pdf_files = list(source_path.glob("**/*.pdf")) + list(source_path.glob("**/*.PDF"))
        
        # DWG files
        dwg_files = list(source_path.glob("**/*.dwg")) + list(source_path.glob("**/*.DWG"))
        
        # DXF files
        dxf_files = list(source_path.glob("**/*.dxf")) + list(source_path.glob("**/*.DXF"))
        
        # Image files (common formats)
        image_extensions = [
            "*.jpg", "*.jpeg", "*.JPG", "*.JPEG",
            "*.png", "*.PNG", 
            "*.tiff", "*.tif", "*.TIFF", "*.TIF",
            "*.bmp", "*.BMP",
            "*.gif", "*.GIF",
            "*.webp", "*.WEBP"
        ]
        
        for ext in image_extensions:
            image_files.extend(list(source_path.glob(f"**/{ext}")))
    
    return [str(f) for f in pdf_files], [str(f) for f in dwg_files], [str(f) for f in dxf_files], [str(f) for f in image_files]

def main():
    """Main function to convert electrical plans to training data"""
    
    parser = argparse.ArgumentParser(description='Convert DWG/PDF/Image electrical plans to training images')
    parser.add_argument('--source', '-s', default='source_files', 
                       help='Source directory containing PDF/DWG/Image files')
    parser.add_argument('--output', '-o', default='extracted_images',
                       help='Output directory for extracted images')
    parser.add_argument('--split', type=float, default=0.8,
                       help='Train/validation split ratio (default: 0.8)')
    
    args = parser.parse_args()
    
    print("⚡ ElectroVision AI - DWG/PDF/Image Training Data Converter")
    print("="*60)
    
    # Setup directories
    setup_directories()
    
    # Scan for source files
    print(f"\n🔍 Scanning for electrical plan files in: {args.source}")
    pdf_files, dwg_files, dxf_files, image_files = scan_source_files(args.source)
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    print(f"📐 Found {len(dwg_files)} DWG files") 
    print(f"📋 Found {len(dxf_files)} DXF files")
    print(f"🖼️ Found {len(image_files)} image files")
    
    if not (pdf_files or dwg_files or dxf_files or image_files):
        print(f"\n⚠️ No electrical plan files found in {args.source}")
        print("📁 Please place your files in:")
        print(f"   • PDF files → {args.source}/pdf/")
        print(f"   • DWG files → {args.source}/dwg/")
        print(f"   • DXF files → {args.source}/dxf/")
        print(f"   • Image files → {args.source}/images/")
        return
    
    all_extracted_images = []
    
    # Process PDF files
    if pdf_files:
        print(f"\n📄 Processing {len(pdf_files)} PDF files...")
        for pdf_file in pdf_files:
            pdf_name = Path(pdf_file).stem
            images = pdf_to_images(pdf_file, args.output, f"pdf_{pdf_name}")
            all_extracted_images.extend(images)
    
    # Process DWG files
    if dwg_files:
        print(f"\n📐 Processing {len(dwg_files)} DWG files...")
        for dwg_file in dwg_files:
            dwg_name = Path(dwg_file).stem
            
            # Convert DWG to DXF first
            dxf_file = dwg_to_dxf(dwg_file, "source_files/dxf")
            
            if dxf_file:
                images = dxf_to_image(dxf_file, args.output, f"dwg_{dwg_name}")
                all_extracted_images.extend(images)
    
    # Process DXF files
    if dxf_files:
        print(f"\n📋 Processing {len(dxf_files)} DXF files...")
        for dxf_file in dxf_files:
            dxf_name = Path(dxf_file).stem
            images = dxf_to_image(dxf_file, args.output, f"dxf_{dxf_name}")
            all_extracted_images.extend(images)
    
    # Process Image files
    if image_files:
        print(f"\n🖼️ Processing {len(image_files)} image files...")
        for image_file in image_files:
            image_name = Path(image_file).stem
            images = process_image_files(image_file, args.output, f"img_{image_name}")
            all_extracted_images.extend(images)
    
    # Organize for training
    if all_extracted_images:
        train_count, val_count = organize_training_data(all_extracted_images, args.split)
        
        print(f"\n🎯 Training Data Summary:")
        print(f"   Total images extracted: {len(all_extracted_images)}")
        print(f"   Training images: {train_count}")
        print(f"   Validation images: {val_count}")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Install annotation tool: pip install labelImg")
        print(f"   2. Annotate images: labelImg dataset/images/train dataset/labels/train")
        print(f"   3. Label electrical components (9 classes):")
        print(f"      0=switch, 1=outlet, 2=light, 3=panel, 4=wire")
        print(f"      5=junction, 6=breaker, 7=ground, 8=measurement")
        print(f"   4. Start training: python train.py")
        
        print(f"\n✅ Ready for annotation and training!")
        
    else:
        print(f"\n❌ No images were successfully extracted.")
        print(f"   Check file formats and try manual conversion if needed.")

if __name__ == "__main__":
    main() 