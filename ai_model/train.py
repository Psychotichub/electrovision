import os
import yaml
import torch
import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import json
import shutil
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

class ElectricalComponentTrainer:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.load_config()
        self.setup_directories()
        
    def load_config(self):
        """Load training configuration"""
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Set default values if not in config
        self.config.setdefault('epochs', 100)
        self.config.setdefault('batch_size', 16)
        self.config.setdefault('img_size', 640)
        self.config.setdefault('workers', 8)
        self.config.setdefault('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        
    def setup_directories(self):
        """Create necessary directories for training"""
        self.base_dir = Path('dataset')
        self.train_dir = self.base_dir / 'images' / 'train'
        self.val_dir = self.base_dir / 'images' / 'val'
        self.train_labels_dir = self.base_dir / 'labels' / 'train'
        self.val_labels_dir = self.base_dir / 'labels' / 'val'
        
        # Create directories
        for dir_path in [self.train_dir, self.val_dir, self.train_labels_dir, self.val_labels_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def prepare_dataset(self, raw_data_dir):
        """Prepare dataset for training"""
        print("📂 Preparing dataset...")
        
        raw_data_path = Path(raw_data_dir)
        if not raw_data_path.exists():
            print(f"❌ Raw data directory not found: {raw_data_dir}")
            return False
            
        # Process PDF extracted images
        pdf_images_dir = raw_data_path / 'pdf_images'
        if pdf_images_dir.exists():
            self.process_pdf_images(pdf_images_dir)
            
        # Process DXF converted images
        dxf_images_dir = raw_data_path / 'dxf_images'
        if dxf_images_dir.exists():
            self.process_dxf_images(dxf_images_dir)
            
        print(f"✅ Dataset prepared successfully!")
        return True
        
    def process_pdf_images(self, pdf_images_dir):
        """Process images extracted from PDFs"""
        print("📄 Processing PDF images...")
        
        for pdf_img_path in pdf_images_dir.glob('*.png'):
            # Basic image preprocessing
            img = cv2.imread(str(pdf_img_path))
            if img is None:
                continue
                
            # Enhance contrast for better component detection
            enhanced_img = self.enhance_image(img)
            
            # Save to training directory
            dest_path = self.train_dir / pdf_img_path.name
            cv2.imwrite(str(dest_path), enhanced_img)
            
            # Create empty label file (to be annotated manually)
            label_path = self.train_labels_dir / f"{pdf_img_path.stem}.txt"
            label_path.touch()
            
    def process_dxf_images(self, dxf_images_dir):
        """Process images converted from DXF files"""
        print("📐 Processing DXF images...")
        
        for dxf_img_path in dxf_images_dir.glob('*.png'):
            img = cv2.imread(str(dxf_img_path))
            if img is None:
                continue
                
            # DXF images might need different preprocessing
            processed_img = self.preprocess_dxf_image(img)
            
            dest_path = self.val_dir / dxf_img_path.name
            cv2.imwrite(str(dest_path), processed_img)
            
            # Create empty label file
            label_path = self.val_labels_dir / f"{dxf_img_path.stem}.txt"
            label_path.touch()
            
    def enhance_image(self, img):
        """Enhance image contrast and clarity"""
        # Convert to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge channels and convert back to BGR
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
        
    def preprocess_dxf_image(self, img):
        """Preprocess DXF converted images"""
        # Convert to grayscale for better line detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply morphological operations to clean up lines
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to BGR
        processed = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
        
        return processed
        
    def create_annotation_guidelines(self):
        """Create annotation guidelines for the team"""
        guidelines = {
            "electrical_components": {
                "switch": {
                    "description": "Light switches, toggle switches, push buttons",
                    "typical_shapes": ["rectangular", "circular"],
                    "annotation_tips": "Include the switch symbol and mounting box"
                },
                "outlet": {
                    "description": "Electrical outlets, sockets, receptacles",
                    "typical_shapes": ["rectangular", "circular with slots"],
                    "annotation_tips": "Include both the outlet symbol and any ground symbols"
                },
                "light": {
                    "description": "Light fixtures, lamps, ceiling lights",
                    "typical_shapes": ["circular", "linear", "custom symbols"],
                    "annotation_tips": "Include the entire fixture symbol"
                },
                "panel": {
                    "description": "Electrical panels, distribution boards",
                    "typical_shapes": ["rectangular", "square"],
                    "annotation_tips": "Include the entire panel outline and label"
                },
                "wire": {
                    "description": "Electrical wires, cables, conduits",
                    "typical_shapes": ["lines", "curves"],
                    "annotation_tips": "Annotate wire segments, not individual pixels"
                },
                "junction": {
                    "description": "Wire junctions, connection points",
                    "typical_shapes": ["dots", "small circles"],
                    "annotation_tips": "Mark clear connection points"
                },
                "breaker": {
                    "description": "Circuit breakers, fuses",
                    "typical_shapes": ["rectangular", "circular"],
                    "annotation_tips": "Include rating labels if visible"
                },
                "ground": {
                    "description": "Ground symbols, earth connections",
                    "typical_shapes": ["triangular", "horizontal lines"],
                    "annotation_tips": "Include the complete ground symbol"
                },
                "measurement": {
                    "description": "Voltage, amperage, power measurements",
                    "typical_shapes": ["text", "numbers with units"],
                    "annotation_tips": "Include the entire measurement text"
                }
            },
            "annotation_tools": [
                "LabelImg - For bounding box annotations",
                "CVAT - For online collaborative annotation",
                "Roboflow - For dataset management and augmentation"
            ],
            "quality_guidelines": [
                "Ensure bounding boxes are tight around objects",
                "Double-check class labels",
                "Annotate all visible components consistently",
                "Use consistent naming conventions"
            ]
        }
        
        with open('annotation_guidelines.json', 'w') as f:
            json.dump(guidelines, f, indent=2)
            
        print("📋 Annotation guidelines created: annotation_guidelines.json")
        
    def train_model(self):
        """Train the YOLO model"""
        print("🚀 Starting model training...")
        
        # Initialize YOLO model
        model = YOLO('yolov8n.pt')  # Start with nano model for faster training
        
        # Train the model
        results = model.train(
            data=self.config_path,
            epochs=self.config['epochs'],
            imgsz=self.config['img_size'],
            batch=self.config.get('batch_size', 16),
            workers=self.config.get('workers', 8),
            device=self.config['device'],
            project='runs/train',
            name='electrical_components',
            save=True,
            plots=True,
            val=True
        )
        
        print("✅ Training completed!")
        return results
        
    def validate_model(self, model_path='runs/train/electrical_components/weights/best.pt'):
        """Validate the trained model"""
        print("🔍 Validating model...")
        
        model = YOLO(model_path)
        
        # Run validation
        metrics = model.val()
        
        # Print validation results
        print(f"📊 Validation Results:")
        print(f"   mAP50: {metrics.box.map50:.3f}")
        print(f"   mAP50-95: {metrics.box.map:.3f}")
        print(f"   Precision: {metrics.box.mp:.3f}")
        print(f"   Recall: {metrics.box.mr:.3f}")
        
        return metrics
        
    def test_inference(self, model_path='runs/train/electrical_components/weights/best.pt', 
                      test_image_path=None):
        """Test model inference on a sample image"""
        print("🧪 Testing model inference...")
        
        model = YOLO(model_path)
        
        # Use a sample image from validation set if none provided
        if test_image_path is None:
            val_images = list(self.val_dir.glob('*.png'))
            if val_images:
                test_image_path = str(val_images[0])
            else:
                print("❌ No test images found")
                return
                
        # Run inference
        results = model(test_image_path)
        
        # Save results
        for r in results:
            r.save(filename=f'test_results/{Path(test_image_path).stem}_predicted.jpg')
            
        print(f"✅ Inference test completed. Results saved to test_results/")
        
    def export_model(self, model_path='runs/train/electrical_components/weights/best.pt'):
        """Export model to different formats"""
        print("📦 Exporting model...")
        
        model = YOLO(model_path)
        
        # Export to ONNX for production deployment
        model.export(format='onnx')
        
        # Export to TensorRT for GPU acceleration
        try:
            model.export(format='engine')
            print("✅ TensorRT export successful")
        except Exception as e:
            print(f"⚠️ TensorRT export failed: {e}")
            
        print("✅ Model export completed!")

def main():
    """Main training pipeline"""
    print("⚡ ElectroVision AI - Training Pipeline")
    print("=" * 50)
    
    # Initialize trainer
    trainer = ElectricalComponentTrainer()
    
    # Create annotation guidelines
    trainer.create_annotation_guidelines()
    
    # Prepare dataset (uncomment when you have raw data)
    # trainer.prepare_dataset('raw_data')
    
    # Train model
    print("\n🎯 Starting training process...")
    print("Note: Make sure you have annotated images in the dataset directory")
    
    # Check if dataset exists
    if not any(trainer.train_dir.glob('*.png')) and not any(trainer.train_dir.glob('*.jpg')):
        print("⚠️ No training images found!")
        print("Please add images to:", trainer.train_dir)
        print("And corresponding labels to:", trainer.train_labels_dir)
        print("Use the annotation guidelines to properly label your data.")
        return
        
    # Train the model
    results = trainer.train_model()
    
    # Validate the model
    trainer.validate_model()
    
    # Test inference
    trainer.test_inference()
    
    # Export model
    trainer.export_model()
    
    print("\n🎉 Training pipeline completed successfully!")
    print("Your trained model is ready for deployment!")

if __name__ == '__main__':
    main()
