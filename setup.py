#!/usr/bin/env python3
"""
ElectroVision AI - Setup Script
Installation and configuration script for the ElectroVision AI project
"""

from setuptools import setup, find_packages
import subprocess
import sys
import os
from pathlib import Path

def install_system_dependencies():
    """Install system-level dependencies"""
    print("Installing system dependencies...")
    
    # Check if Tesseract is installed
    try:
        subprocess.run(['tesseract', '--version'], check=True, capture_output=True)
        print("✅ Tesseract OCR is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract OCR not found. Please install it:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    return True

def setup_directories():
    """Create necessary project directories"""
    directories = [
        'data/raw',
        'data/processed',
        'data/datasets/train/images',
        'data/datasets/train/labels',
        'data/datasets/val/images',
        'data/datasets/val/labels',
        'models/checkpoints',
        'models/exports',
        'logs',
        'results',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created project directories")

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("Installing Node.js dependencies...")
    
    try:
        # Backend dependencies
        subprocess.run(['npm', 'install'], cwd='backend', check=True)
        print("✅ Backend dependencies installed")
        
        # Frontend dependencies
        subprocess.run(['npm', 'install'], cwd='frontend', check=True)
        print("✅ Frontend dependencies installed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    
    return True

def download_yolo_weights():
    """Download pre-trained YOLO weights"""
    print("Downloading YOLO weights...")
    
    try:
        from ultralytics import YOLO
        
        # Download YOLOv8 nano model
        model = YOLO('yolov8n.pt')
        print("✅ YOLOv8 nano weights downloaded")
        
        # Download YOLOv8 small model
        model = YOLO('yolov8s.pt')
        print("✅ YOLOv8 small weights downloaded")
        
    except Exception as e:
        print(f"❌ Failed to download YOLO weights: {e}")
        return False
    
    return True

def create_config_files():
    """Create configuration files"""
    
    # Create .env file for backend
    env_content = """# ElectroVision AI Configuration
PORT=3000
NODE_ENV=development
UPLOAD_DIR=uploads
PYTHON_CMD=python
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=.pdf,.dwg,.dxf
CORS_ORIGIN=http://localhost:3001
LOG_LEVEL=info
"""
    
    with open('backend/.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created configuration files")

def main():
    """Main setup function"""
    print("⚡ ElectroVision AI Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detected")
    
    # Install system dependencies
    if not install_system_dependencies():
        print("⚠️ Some system dependencies are missing. Please install them manually.")
    
    # Create directories
    setup_directories()
    
    # Install Node.js dependencies
    if not install_node_dependencies():
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    # Create config files
    create_config_files()
    
    # Download YOLO weights
    if not download_yolo_weights():
        print("⚠️ Failed to download YOLO weights. You can download them later.")
    
    print("\n🎉 ElectroVision AI setup completed successfully!")
    print("\nNext steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Start the backend: cd backend && npm start")
    print("3. Start the frontend: cd frontend && npm start")
    print("4. Open http://localhost:3001 in your browser")
    print("\nFor training the AI model:")
    print("1. Prepare your dataset using data-prep/extract_from_pdf.py")
    print("2. Annotate your images using tools like LabelImg or CVAT")
    print("3. Train the model: cd ai_model && python train.py")

if __name__ == "__main__":
    main()

# Package setup configuration
setup(
    name="electrovision-ai",
    version="1.0.0",
    description="AI-Powered Electrical Plan Interpreter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Psychotic",
    author_email="psychotic@example.com",
    url="https://github.com/psychotic/electrovision-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.3.3",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "ezdxf>=1.1.4",
        "PyMuPDF>=1.23.8",
        "pdfplumber>=0.10.3",
        "ultralytics>=8.0.224",
        "opencv-python>=4.8.1.78",
        "pillow>=10.1.0",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "matplotlib>=3.7.2",
        "seaborn>=0.12.2",
        "scikit-learn>=1.3.0",
        "torch>=2.0.1",
        "torchvision>=0.15.2",
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "shapely>=2.0.2",
        "scipy>=1.11.3",
        "networkx>=3.1",
        "plotly>=5.17.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "tqdm>=4.66.1",
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "watchdog>=3.0.0",
    ],
    extras_require={
        "tensorflow": ["tensorflow>=2.13.0"],
        "jupyter": ["jupyter>=1.0.0", "notebook>=7.0.6", "ipywidgets>=8.1.1"],
        "dev": ["pytest>=7.4.3", "black>=23.11.0", "flake8>=6.1.0"],
    },
    entry_points={
        "console_scripts": [
            "electrovision-extract=data_prep.extract_from_pdf:main",
            "electrovision-convert=data_prep.format_converter:main",
            "electrovision-train=ai_model.train:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 