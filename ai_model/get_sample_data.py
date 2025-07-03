#!/usr/bin/env python3
"""
🔄 ElectroVision AI - Sample Data Downloader

This script helps you get started by downloading sample electrical plan images
that you can use for annotation and training.
"""

import os
import requests
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def create_directories():
    """Create necessary directories for training data"""
    dirs = [
        "dataset/images/train",
        "dataset/images/val", 
        "dataset/labels/train",
        "dataset/labels/val"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Created dataset directories")

def create_sample_electrical_plan(filename, width=800, height=600):
    """Create a synthetic electrical plan image with components"""
    
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw room outline
    draw.rectangle([50, 50, width-50, height-50], outline='black', width=3)
    
    # Add electrical components
    components = []
    
    # Switch (rectangle with S)
    switch_x, switch_y = 150, 100
    draw.rectangle([switch_x-15, switch_y-10, switch_x+15, switch_y+10], 
                   outline='black', width=2)
    draw.text((switch_x-5, switch_y-8), 'S', fill='black')
    components.append((0, switch_x, switch_y, 30, 20))  # class 0 = switch
    
    # Outlet (rectangle with two circles)
    outlet_x, outlet_y = 300, 150
    draw.rectangle([outlet_x-15, outlet_y-10, outlet_x+15, outlet_y+10], 
                   outline='black', width=2)
    draw.ellipse([outlet_x-8, outlet_y-5, outlet_x-3, outlet_y], outline='black')
    draw.ellipse([outlet_x+3, outlet_y-5, outlet_x+8, outlet_y], outline='black')
    components.append((1, outlet_x, outlet_y, 30, 20))  # class 1 = outlet
    
    # Light fixture (circle)
    light_x, light_y = 400, 300
    draw.ellipse([light_x-20, light_y-20, light_x+20, light_y+20], 
                 outline='black', width=2)
    draw.text((light_x-5, light_y-8), 'L', fill='black')
    components.append((2, light_x, light_y, 40, 40))  # class 2 = light
    
    # Electrical panel (large rectangle)
    panel_x, panel_y = 100, 400
    draw.rectangle([panel_x-30, panel_y-40, panel_x+30, panel_y+40], 
                   outline='black', width=3)
    draw.text((panel_x-10, panel_y-5), 'PANEL', fill='black')
    components.append((3, panel_x, panel_y, 60, 80))  # class 3 = panel
    
    # Wires (lines connecting components)
    draw.line([switch_x+15, switch_y, light_x-20, light_y], fill='black', width=2)
    draw.line([outlet_x, outlet_y+10, outlet_x, outlet_y+50], fill='black', width=2)
    wire_points = [(switch_x+15, switch_y), (light_x-20, light_y)]
    components.append((4, (wire_points[0][0] + wire_points[1][0])//2, 
                      (wire_points[0][1] + wire_points[1][1])//2, 200, 5))  # class 4 = wire
    
    # Junction (small filled circle)
    junction_x, junction_y = 250, 200
    draw.ellipse([junction_x-5, junction_y-5, junction_x+5, junction_y+5], 
                 fill='black')
    components.append((5, junction_x, junction_y, 10, 10))  # class 5 = junction
    
    # Ground symbol (triangle)
    ground_x, ground_y = 500, 500
    points = [(ground_x, ground_y-10), (ground_x-10, ground_y+10), (ground_x+10, ground_y+10)]
    draw.polygon(points, outline='black', width=2)
    components.append((7, ground_x, ground_y, 20, 20))  # class 7 = ground
    
    # Save image
    img.save(filename)
    
    return components

def create_yolo_label(components, img_width, img_height, label_filename):
    """Create YOLO format label file"""
    
    with open(label_filename, 'w') as f:
        for class_id, center_x, center_y, width, height in components:
            # Normalize coordinates to 0-1 range
            norm_center_x = center_x / img_width
            norm_center_y = center_y / img_height
            norm_width = width / img_width
            norm_height = height / img_height
            
            f.write(f"{class_id} {norm_center_x:.6f} {norm_center_y:.6f} "
                   f"{norm_width:.6f} {norm_height:.6f}\n")

def generate_sample_dataset(num_images=10):
    """Generate synthetic electrical plan images with labels"""
    
    print(f"🎨 Generating {num_images} sample electrical plan images...")
    
    for i in range(num_images):
        # Vary image dimensions slightly
        width = random.randint(600, 1000)
        height = random.randint(400, 800)
        
        # Create image filename
        img_filename = f"dataset/images/train/sample_plan_{i+1:03d}.jpg"
        label_filename = f"dataset/labels/train/sample_plan_{i+1:03d}.txt"
        
        # Generate image and get component locations
        components = create_sample_electrical_plan(img_filename, width, height)
        
        # Create corresponding YOLO label file
        create_yolo_label(components, width, height, label_filename)
        
        print(f"  ✅ Created {img_filename} with {len(components)} components")
    
    print(f"🎉 Generated {num_images} sample images with annotations!")

def download_annotation_tool():
    """Provide instructions for downloading LabelImg"""
    
    print("\n🛠️ Annotation Tool Installation:")
    print("   pip install labelImg")
    print("   labelImg dataset/images/train dataset/labels/train")
    print("\n📋 Instructions:")
    print("   1. Open LabelImg")
    print("   2. Set save format to 'YOLO'")
    print("   3. Open directory: dataset/images/train")
    print("   4. Draw bounding boxes around electrical components")
    print("   5. Select correct class for each component")

def main():
    """Main function to set up sample training data"""
    
    print("⚡ ElectroVision AI - Sample Data Setup")
    print("="*50)
    
    # Create directory structure
    create_directories()
    
    # Generate sample images
    generate_sample_dataset(num_images=15)
    
    # Create a few validation images too
    print("\n🔄 Creating validation dataset...")
    for i in range(3):
        width = random.randint(600, 1000)
        height = random.randint(400, 800)
        
        img_filename = f"dataset/images/val/val_plan_{i+1:03d}.jpg"
        label_filename = f"dataset/labels/val/val_plan_{i+1:03d}.txt"
        
        components = create_sample_electrical_plan(img_filename, width, height)
        create_yolo_label(components, width, height, label_filename)
    
    print("✅ Created 3 validation images")
    
    # Show next steps
    print("\n🎯 Next Steps:")
    print("   1. Review generated images in: dataset/images/train/")
    print("   2. Check label files in: dataset/labels/train/")
    print("   3. Install LabelImg: pip install labelImg")
    print("   4. Add your own electrical plan images")
    print("   5. Run training: python train.py")
    
    download_annotation_tool()
    
    print("\n🚀 Ready to start training your AI model!")

if __name__ == "__main__":
    main() 