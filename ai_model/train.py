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
        self.print_gpu_info()
        self.configure_gpu()
        self.load_config()
        self.setup_directories()
        
    def print_gpu_info(self):
        """Print comprehensive GPU information"""
        print("\n" + "="*60)
        print("🔥 GPU CONFIGURATION CHECK")
        print("="*60)
        
        # System info
        print(f"🖥️  System: {torch.version.cuda}")
        print(f"🐍 PyTorch version: {torch.__version__}")
        
        # CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"⚡ CUDA available: {cuda_available}")
        
        if cuda_available:
            print(f"🎯 CUDA version: {torch.version.cuda}")
            print(f"📊 Number of GPUs: {torch.cuda.device_count()}")
            
            # GPU details
            for i in range(torch.cuda.device_count()):
                gpu_props = torch.cuda.get_device_properties(i)
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = gpu_props.total_memory / (1024**3)  # Convert to GB
                
                print(f"🚀 GPU {i}: {gpu_name}")
                print(f"   💾 Memory: {gpu_memory:.1f} GB")
                print(f"   🔧 Compute Capability: {gpu_props.major}.{gpu_props.minor}")
                print(f"   🏭 Multi-processors: {gpu_props.multi_processor_count}")
                
                # Memory usage
                if i == 0:  # Check memory for primary GPU
                    allocated = torch.cuda.memory_allocated(i) / (1024**3)
                    cached = torch.cuda.memory_reserved(i) / (1024**3)
                    print(f"   📈 Memory Allocated: {allocated:.2f} GB")
                    print(f"   💽 Memory Cached: {cached:.2f} GB")
                    
            # Current device
            current_device = torch.cuda.current_device()
            print(f"🎯 Current CUDA device: {current_device}")
            
            # Test GPU computation
            try:
                print("🧪 Testing GPU computation...")
                start_time = torch.cuda.Event(enable_timing=True)
                end_time = torch.cuda.Event(enable_timing=True)
                
                start_time.record()
                x = torch.rand(1000, 1000, device='cuda')
                y = torch.rand(1000, 1000, device='cuda')
                z = torch.matmul(x, y)
                torch.cuda.synchronize()
                end_time.record()
                
                torch.cuda.synchronize()
                elapsed_time = start_time.elapsed_time(end_time)
                print(f"✅ GPU computation test: PASSED ({elapsed_time:.2f}ms)")
            except Exception as e:
                print(f"❌ GPU computation test: FAILED - {e}")
        else:
            print("❌ No CUDA GPUs detected!")
            print("⚠️  Training will run on CPU (much slower)")
            
        print("="*60)
        
    def configure_gpu(self):
        """Configure GPU settings for optimal training"""
        if torch.cuda.is_available():
            # Set GPU memory growth (helps with memory management)
            torch.cuda.empty_cache()
            
            # Set the primary GPU
            torch.cuda.set_device(0)
            
            # Enable cudnn for better performance
            torch.backends.cudnn.enabled = True
            torch.backends.cudnn.benchmark = True
            
            print("🔧 GPU configuration completed:")
            print(f"   📌 Primary device set to: cuda:0")
            print(f"   🚀 cuDNN enabled: {torch.backends.cudnn.enabled}")
            print(f"   ⚡ cuDNN benchmark: {torch.backends.cudnn.benchmark}")
        else:
            print("⚠️  No GPU configuration applied (CUDA not available)")
        
    def load_config(self):
        """Load training configuration"""
        with open(self.config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        
        # Set default values if not in config
        self.config.setdefault('epochs', 100)
        self.config.setdefault('batch_size', 16)
        self.config.setdefault('img_size', 640)
        self.config.setdefault('workers', 8)
        
        # Force GPU usage if available, with detailed device selection
        if torch.cuda.is_available():
            self.config['device'] = 'cuda:0'  # Explicitly use first GPU
            print(f"✅ Device configured: {self.config['device']} (NVIDIA GPU)")
            
            # Adjust batch size based on GPU memory
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if gpu_memory < 6.0:  # Less than 6GB
                recommended_batch = min(self.config['batch_size'], 8)
                if self.config['batch_size'] > recommended_batch:
                    print(f"⚠️  Reducing batch size from {self.config['batch_size']} to {recommended_batch} for 4GB GPU")
                    self.config['batch_size'] = recommended_batch
        else:
            self.config['device'] = 'cpu'
            print(f"⚠️  Device configured: {self.config['device']} (CPU - will be slow)")
            
        print(f"🎯 Training configuration:")
        print(f"   📊 Epochs: {self.config['epochs']}")
        print(f"   📦 Batch size: {self.config['batch_size']}")
        print(f"   🖼️  Image size: {self.config['img_size']}")
        print(f"   👥 Workers: {self.config['workers']}")
        print(f"   🔧 Device: {self.config['device']}")
        
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
            "annotation_guidelines": {
                "components": {
                    "main_breaker": {
                        "description": "Main circuit breaker for entire panel",
                        "typical_shapes": ["rectangular with label"],
                        "annotation_tips": "Include full body and label (e.g., rating)"
                    },
                    "mcb": {
                        "description": "Miniature Circuit Breaker used for branch circuits",
                        "typical_shapes": ["small rectangle with toggle"],
                        "annotation_tips": "Include full unit and label if visible"
                    },
                    "rccb": {
                        "description": "Residual Current Circuit Breaker for leakage protection",
                        "typical_shapes": ["rectangular with test button"],
                        "annotation_tips": "Annotate test/reset button and device body"
                    },
                    "elcb": {
                        "description": "Earth Leakage Circuit Breaker (older type of RCCB)",
                        "typical_shapes": ["rectangular"],
                        "annotation_tips": "Similar to RCCB — label clearly"
                    },
                    "fuse": {
                        "description": "Electrical fuse for overcurrent protection",
                        "typical_shapes": ["small cylindrical or rectangular"],
                        "annotation_tips": "Include fuse carrier and symbol"
                    },
                    "distribution_panel": {
                        "description": "Electrical distribution board or panel",
                        "typical_shapes": ["large rectangle with multiple breakers"],
                        "annotation_tips": "Include full panel box and labels"
                    },
                    "busbar": {
                        "description": "Conductive bar distributing power",
                        "typical_shapes": ["horizontal or vertical strips"],
                        "annotation_tips": "Highlight copper/metallic lines inside panels"
                    },
                    "isolator": {
                        "description": "Switch used to isolate electrical circuit",
                        "typical_shapes": ["rotary or lever type"],
                        "annotation_tips": "Mark handle and body"
                    },
                    "contactor": {
                        "description": "Electromechanical relay for switching loads",
                        "typical_shapes": ["block with coil and contacts"],
                        "annotation_tips": "Include coil section and terminal layout"
                    },
                    "relay": {
                        "description": "Electromechanical or solid-state relay",
                        "typical_shapes": ["small block with multiple terminals"],
                        "annotation_tips": "Mark full body, include label if present"
                    },
                    "overload_relay": {
                        "description": "Protects motors from overload conditions",
                        "typical_shapes": ["attached below contactors"],
                        "annotation_tips": "Include thermal dial and body"
                    },
                    "spd": {
                        "description": "Surge Protection Device",
                        "typical_shapes": ["box-type with green/red indicator"],
                        "annotation_tips": "Highlight indicator and label"
                    },
                    "timer": {
                        "description": "Used for controlling time-based operations",
                        "typical_shapes": ["circular dial or digital timer"],
                        "annotation_tips": "Include display or dial"
                    },
                    "ct": {
                        "description": "Current Transformer (CT)",
                        "typical_shapes": ["ring or donut shape"],
                        "annotation_tips": "Mark ring and wire passing through"
                    },
                    "pt": {
                        "description": "Potential Transformer (PT)",
                        "typical_shapes": ["small box-type"],
                        "annotation_tips": "Label clearly as PT"
                    },
                    "lightning_arrester": {
                        "description": "Protects system from lightning surge",
                        "typical_shapes": ["tall with finned top"],
                        "annotation_tips": "Include base and top elements"
                    },
                    "wire": {
                        "description": "Single or bundled conductor",
                        "typical_shapes": ["curved or straight lines"],
                        "annotation_tips": "Trace wire path, not background"
                    },
                    "cable": {
                        "description": "Group of wires or armored cable",
                        "typical_shapes": ["thicker lines"],
                        "annotation_tips": "Trace segments from panel to load"
                    },
                    "conduit": {
                        "description": "PVC or metallic pipe carrying cables",
                        "typical_shapes": ["cylindrical tubes"],
                        "annotation_tips": "Include path across walls or ceilings"
                    },
                    "cable_tray": {
                        "description": "Tray supporting multiple cables",
                        "typical_shapes": ["U or ladder shape"],
                        "annotation_tips": "Outline tray frame clearly"
                    },
                    "pull_box": {
                        "description": "Box allowing wire pulling and splicing",
                        "typical_shapes": ["square/rectangular box"],
                        "annotation_tips": "Mark cover and label"
                    },
                    "gland": {
                        "description": "Seal for cable entry",
                        "typical_shapes": ["circular or threaded"],
                        "annotation_tips": "Annotate entry point on panel"
                    },
                    "lug": {
                        "description": "Terminal for cable connection",
                        "typical_shapes": ["U or ring shape"],
                        "annotation_tips": "Highlight where wire meets device"
                    },
                    "busbar_chamber": {
                        "description": "Enclosure housing busbars",
                        "typical_shapes": ["metallic box with bars inside"],
                        "annotation_tips": "Include visible opening and label"
                    },
                    "switch": {
                        "description": "Switch for on/off operation",
                        "typical_shapes": ["rectangular or circular"],
                        "annotation_tips": "Include the actuator and body"
                    },
                    "dimmer_switch": {
                        "description": "Rotary or slider switch for light dimming",
                        "typical_shapes": ["round knob or slider"],
                        "annotation_tips": "Include dial"
                    },
                    "push_button": {
                        "description": "Simple momentary switch",
                        "typical_shapes": ["round or square with label"],
                        "annotation_tips": "Highlight full button head"
                    },
                    "selector_switch": {
                        "description": "Rotary switch with multiple positions",
                        "typical_shapes": ["rotary knob"],
                        "annotation_tips": "Mark knob and base"
                    },
                    "limit_switch": {
                        "description": "Detects motion limits in machinery",
                        "typical_shapes": ["box with arm or plunger"],
                        "annotation_tips": "Include actuator arm"
                    },
                    "float_switch": {
                        "description": "Liquid level control switch",
                        "typical_shapes": ["elongated float"],
                        "annotation_tips": "Mark float and wire"
                    },
                    "rotary_switch": {
                        "description": "Rotating knob for mode selection",
                        "typical_shapes": ["round dial"],
                        "annotation_tips": "Mark pointer and positions"
                    },
                    "emergency_stop": {
                        "description": "Red mushroom-type push button",
                        "typical_shapes": ["round with red top"],
                        "annotation_tips": "Always annotate full visible area"
                    },
                    "led_light": {
                        "description": "LED fixture or indicator",
                        "typical_shapes": ["small circles", "panels"],
                        "annotation_tips": "Mark the whole LED shape"
                    },
                    "incandescent_bulb": {
                        "description": "Traditional bulb type",
                        "typical_shapes": ["bulb shape"],
                        "annotation_tips": "Include filament and base"
                    },
                    "tube_light": {
                        "description": "Fluorescent or LED tube",
                        "typical_shapes": ["long rectangle"],
                        "annotation_tips": "Include holders if visible"
                    },
                    "flood_light": {
                        "description": "High-intensity lighting fixture",
                        "typical_shapes": ["wide cone or square"],
                        "annotation_tips": "Annotate fixture housing"
                    },
                    "street_light": {
                        "description": "Pole-mounted outdoor light",
                        "typical_shapes": ["curved pole and head"],
                        "annotation_tips": "Mark pole + fixture"
                    },
                    "motion_sensor_light": {
                        "description": "Light with motion detection",
                        "typical_shapes": ["fixture with sensor dome"],
                        "annotation_tips": "Highlight sensor and lamp"
                    },
                    "emergency_light": {
                        "description": "Backup light during power failure",
                        "typical_shapes": ["rectangular or twin lamp"],
                        "annotation_tips": "Include battery box if visible"
                    },
                    "power_socket": {
                        "description": "Standard wall socket",
                        "typical_shapes": ["rectangular with holes"],
                        "annotation_tips": "Include full faceplate"
                    },
                    "industrial_socket": {
                        "description": "Heavy-duty socket (3-phase etc.)",
                        "typical_shapes": ["round with flap"],
                        "annotation_tips": "Highlight pins and cover"
                    },
                    "earth_rod": {
                        "description": "Metal rod buried for grounding",
                        "typical_shapes": ["vertical stick"],
                        "annotation_tips": "Include top part and wire"
                    },
                    "earthing_wire": {
                        "description": "Green/yellow wire connected to ground",
                        "typical_shapes": ["line"],
                        "annotation_tips": "Trace full path"
                    },
                    "earth_pit": {
                        "description": "Underground grounding point",
                        "typical_shapes": ["square or round cover"],
                        "annotation_tips": "Mark lid and label"
                    },
                    "earth_busbar": {
                        "description": "Grounding bar inside panel",
                        "typical_shapes": ["flat strip with wires"],
                        "annotation_tips": "Highlight all terminals"
                    },
                    "earth_terminal": {
                        "description": "Terminal block for earth wire",
                        "typical_shapes": ["screw-type terminal"],
                        "annotation_tips": "Include mounting point"
                    },
                    "lightning_protection": {
                        "description": "External system for lightning discharge",
                        "typical_shapes": ["rod on roof"],
                        "annotation_tips": "Annotate full rod and path"
                    },
                    "voltmeter": {
                        "description": "Measures voltage",
                        "typical_shapes": ["digital or analog gauge"],
                        "annotation_tips": "Include screen/dial"
                    },
                    "ammeter": {
                        "description": "Measures current (A)",
                        "typical_shapes": ["analog/digital"],
                        "annotation_tips": "Mark full display"
                    },
                    "power_meter": {
                        "description": "Measures real power (kW)",
                        "typical_shapes": ["digital display"],
                        "annotation_tips": "Include nameplate"
                    },
                    "energy_meter": {
                        "description": "Tracks energy usage (kWh)",
                        "typical_shapes": ["glass-covered display"],
                        "annotation_tips": "Include full box"
                    },
                    "multifunction_meter": {
                        "description": "Measures voltage, current, power, etc.",
                        "typical_shapes": ["LCD display with buttons"],
                        "annotation_tips": "Mark screen and buttons"
                    },
                    "frequency_meter": {
                        "description": "Measures frequency (Hz)",
                        "typical_shapes": ["gauge or digital"],
                        "annotation_tips": "Include unit scale"
                    },
                    "power_factor_meter": {
                        "description": "Indicates power factor",
                        "typical_shapes": ["dial or screen"],
                        "annotation_tips": "Label axis if visible"
                    }
                },
                "tools": ["LabelImg", "CVAT", "Roboflow"],
                "general_guidelines": [
                    "Keep boxes tight around the object",
                    "Do not include background clutter",
                    "Be consistent with naming",
                    "Label only visible components",
                    "Avoid overlapping boxes unless required"
                ]
            }
        }
        
        with open('annotation_guidelines.json', 'w') as f:
            json.dump(guidelines, f, indent=2)
            
        print("📋 Annotation guidelines created: annotation_guidelines.json")
        
    def train_model(self):
        """Train the YOLO model with dynamic validation handling and GPU optimization"""
        print("\n" + "="*60)
        print("🚀 STARTING MODEL TRAINING")
        print("="*60)
        
        # Check validation data availability first
        use_validation = self.check_validation_data()
        
        # Create dynamic configuration
        dynamic_config_path = self.create_dynamic_config(use_validation)
        
        # Pre-training GPU check and optimization
        if torch.cuda.is_available():
            print("🔥 GPU Training Status:")
            print(f"   🎯 Using device: {self.config['device']}")
            print(f"   🚀 GPU Name: {torch.cuda.get_device_name(0)}")
            
            # Clear GPU cache before training
            torch.cuda.empty_cache()
            
            # Force GPU memory cleanup
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
            
            # Check GPU memory before training
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_memory_cached = torch.cuda.memory_reserved(0) / (1024**3)
            
            print(f"   💾 GPU Memory Status:")
            print(f"      Total: {gpu_memory_total:.1f} GB")
            print(f"      Allocated: {gpu_memory_allocated:.2f} GB")
            print(f"      Cached: {gpu_memory_cached:.2f} GB")
            print(f"      Free: {gpu_memory_total - gpu_memory_allocated:.2f} GB")
            
            # Optimize batch size for GPU memory
            if gpu_memory_total < 8.0:  # Less than 8GB
                recommended_batch = min(self.config['batch_size'], 8)
                if self.config['batch_size'] > recommended_batch:
                    print(f"   ⚡ Optimizing batch size from {self.config['batch_size']} to {recommended_batch} for GPU memory")
                    self.config['batch_size'] = recommended_batch
            
            # GPU utilization test
            try:
                print("🧪 Final GPU test before training...")
                test_tensor = torch.rand(1000, 1000, device=self.config['device'])
                result = test_tensor @ test_tensor.T
                torch.cuda.synchronize()
                print("✅ GPU ready for training!")
                del test_tensor, result
                torch.cuda.empty_cache()
            except Exception as e:
                print(f"❌ GPU test failed: {e}")
                print("⚠️  Falling back to CPU training")
                self.config['device'] = 'cpu'
        else:
            print("⚠️  Training on CPU (no GPU available)")
            print("   💡 Consider using a system with NVIDIA GPU for faster training")
        
        print("="*60)
        
        # Initialize YOLO model with explicit device setting
        print("📦 Initializing YOLO model...")
        model = YOLO('yolov8n.pt')  # Start with nano model for faster training
        
        # Force model to GPU if available
        if torch.cuda.is_available() and self.config['device'].startswith('cuda'):
            try:
                # Ensure model is on the correct device
                model.to(self.config['device'])
                print(f"✅ Model loaded on: {self.config['device']}")
            except Exception as e:
                print(f"⚠️  Could not move model to GPU: {e}")
                self.config['device'] = 'cpu'
        
        print("🎯 Training Parameters:")
        print(f"   📊 Epochs: {self.config['epochs']}")
        print(f"   📦 Batch size: {self.config['batch_size']}")
        print(f"   🖼️  Image size: {self.config['img_size']}")
        print(f"   👥 Workers: {self.config['workers']}")
        print(f"   🔧 Device: {self.config['device']}")
        print(f"   🎯 Validation: {'Enabled' if use_validation else 'Disabled (no valid data)'}")
        print(f"   📁 Config: {dynamic_config_path}")
        
        print("\n🏁 Training starting now...")
        print("="*60)
        
        # Train the model with optimized parameters
        try:
            results = model.train(
                data=dynamic_config_path,  # Use dynamic config
                epochs=self.config['epochs'],
                imgsz=self.config['img_size'],
                batch=self.config.get('batch_size', 16),
                workers=self.config.get('workers', 8),
                device=self.config['device'],  # Explicit GPU device
                project='runs/train',
                name='electrical_components',
                save=True,
                plots=True,
                val=use_validation,  # Dynamic validation setting
                verbose=True,
                # GPU optimization parameters - disable AMP if issues
                amp=False,  # Disable AMP to avoid torchvision CUDA issues
                cache=False,  # Avoid caching to save GPU memory
                single_cls=False,
                optimizer='AdamW',
                lr0=0.01,
                patience=50,
                save_period=10
            )
            
        except NotImplementedError as e:
            if "torchvision::nms" in str(e) and "CUDA" in str(e):
                print(f"\n❌ TORCHVISION CUDA COMPATIBILITY ERROR!")
                print(f"   🔧 Issue: torchvision doesn't have CUDA support for NMS operations")
                print(f"   💡 This is a common PyTorch/torchvision version mismatch")
                print(f"\n🔄 Attempting training with CPU fallback for NMS...")
                
                # Try with CPU device to avoid CUDA NMS issues
                print(f"   📝 Switching to CPU training to avoid torchvision CUDA issues")
                self.config['device'] = 'cpu'
                torch.cuda.empty_cache()  # Clear GPU memory
                
                results = model.train(
                    data=dynamic_config_path,
                    epochs=self.config['epochs'],
                    imgsz=self.config['img_size'],
                    batch=self.config.get('batch_size', 16),
                    workers=self.config.get('workers', 8),
                    device='cpu',  # Force CPU
                    project='runs/train',
                    name='electrical_components',
                    save=True,
                    plots=True,
                    val=use_validation,
                    verbose=True,
                    amp=False,
                    cache=False
                )
                
                print(f"\n⚠️  TRAINING COMPLETED ON CPU")
                print(f"   🔧 To fix this for future GPU training:")
                print(f"   1. Reinstall PyTorch and torchvision with matching CUDA versions:")
                print(f"      pip uninstall torch torchvision")
                print(f"      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
                print(f"   2. Or use: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
                
            else:
                raise e
                
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"\n❌ GPU OUT OF MEMORY ERROR!")
                print(f"   💾 Try reducing batch size (current: {self.config['batch_size']})")
                print(f"   💾 Current GPU memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
                print(f"   💡 Suggestion: Reduce batch_size to 4 or 8 in config.yaml")
                
                # Try with reduced batch size automatically
                print(f"\n🔄 Attempting training with reduced batch size...")
                reduced_batch = max(1, self.config['batch_size'] // 2)
                print(f"   📦 Reducing batch size to: {reduced_batch}")
                
                torch.cuda.empty_cache()  # Clear memory
                
                results = model.train(
                    data=dynamic_config_path,
                    epochs=self.config['epochs'],
                    imgsz=self.config['img_size'],
                    batch=reduced_batch,  # Reduced batch size
                    workers=self.config.get('workers', 8),
                    device=self.config['device'],
                    project='runs/train',
                    name='electrical_components',
                    save=True,
                    plots=True,
                    val=use_validation,
                    verbose=True,
                    amp=False,  # Disable AMP
                    cache=False
                )
            else:
                raise e
        
        # Post-training GPU status
        if torch.cuda.is_available() and self.config['device'].startswith('cuda'):
            print("\n" + "="*60)
            print("🏆 TRAINING COMPLETED - GPU STATUS")
            print("="*60)
            
            final_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            final_cached = torch.cuda.memory_reserved(0) / (1024**3)
            
            print(f"🎯 Final GPU Memory Usage:")
            print(f"   Allocated: {final_allocated:.2f} GB")
            print(f"   Cached: {final_cached:.2f} GB")
            
            # Clean up GPU memory
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print("🧹 GPU cache cleared")
            print("="*60)
        
        # Clean up dynamic config file
        try:
            os.remove(dynamic_config_path)
            print(f"🧹 Cleaned up temporary config: {dynamic_config_path}")
        except:
            pass
            
        print("✅ Training completed successfully!")
        
        if not use_validation:
            print("⚠️  Note: Training completed without validation.")
            print("   Consider adding validation data for better model evaluation.")
            
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

    def split_training_data_for_validation(self, validation_ratio=0.2):
        """Split some training data to create validation set"""
        print(f"📊 Creating validation set from training data ({validation_ratio*100}% split)...")
        
        # Get all training images
        train_image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
        train_images = []
        for ext in train_image_extensions:
            train_images.extend(list(self.train_dir.glob(ext)))
        
        if len(train_images) == 0:
            print("❌ No training images found to split!")
            return False
        
        # Calculate split
        num_val_images = int(len(train_images) * validation_ratio)
        if num_val_images == 0:
            print("⚠️  Too few images to create validation split!")
            return False
        
        # Randomly select images for validation
        import random
        random.shuffle(train_images)
        val_images = train_images[:num_val_images]
        
        print(f"   📁 Moving {len(val_images)} images to validation...")
        
        # Move images and corresponding labels
        moved_count = 0
        for img_path in val_images:
            # Move image
            val_img_path = self.val_dir / img_path.name
            shutil.move(str(img_path), str(val_img_path))
            
            # Move corresponding label if it exists
            label_path = self.train_labels_dir / f"{img_path.stem}.txt"
            if label_path.exists():
                val_label_path = self.val_labels_dir / f"{img_path.stem}.txt"
                shutil.move(str(label_path), str(val_label_path))
            
            moved_count += 1
        
        print(f"✅ Successfully created validation set with {moved_count} images")
        return True

    def check_validation_data(self):
        """Check if validation data exists and is usable"""
        print("🔍 Checking validation data...")
        
        # Check for validation images
        val_image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
        val_images = []
        for ext in val_image_extensions:
            val_images.extend(list(self.val_dir.glob(ext)))
        
        # Check for validation labels
        val_labels = list(self.val_labels_dir.glob('*.txt'))
        
        print(f"   📁 Validation images found: {len(val_images)}")
        print(f"   🏷️  Validation labels found: {len(val_labels)}")
        
        # Check if labels have actual content (not just empty files)
        valid_labels = 0
        for label_file in val_labels:
            if label_file.stat().st_size > 0:  # File has content
                valid_labels += 1
        
        print(f"   ✅ Valid labels (with content): {valid_labels}")
        
        # Determine if validation data is usable
        has_valid_data = len(val_images) > 0 and valid_labels > 0
        
        if has_valid_data:
            print("   🎯 Validation data available - will use for training")
        else:
            print("   ⚠️  No valid validation data found - will skip validation")
            
        return has_valid_data
    
    def create_dynamic_config(self, use_validation=True):
        """Create a dynamic config file based on validation data availability"""
        config_data = {
            'train': str(self.base_dir / 'images' / 'train'),
            'nc': self.config.get('nc', 77),
            'names': self.config.get('names', {})
        }
        
        if use_validation:
            config_data['val'] = str(self.base_dir / 'images' / 'val')
            print("   ✅ Config created with validation path")
        else:
            # Point validation to training data to avoid YOLO errors
            config_data['val'] = str(self.base_dir / 'images' / 'train')
            print("   ⚠️  Config created without separate validation (using training data)")
        
        # Save dynamic config
        dynamic_config_path = 'dataset_dynamic.yaml'
        with open(dynamic_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False)
            
        print(f"   📝 Dynamic config saved to: {dynamic_config_path}")
        return dynamic_config_path

    def check_gpu_setup(self):
        """Comprehensive GPU setup check"""
        print("\n🔍 GPU Setup Verification:")
        print("="*50)
        
        # Check PyTorch CUDA
        print(f"1. PyTorch version: {torch.__version__}")
        print(f"2. CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"3. CUDA version: {torch.version.cuda}")
            print(f"4. cuDNN version: {torch.backends.cudnn.version()}")
            print(f"5. GPU count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            
            # Test GPU computation
            try:
                x = torch.rand(100, 100, device='cuda')
                y = x @ x.T
                print("6. ✅ GPU computation test: PASSED")
            except Exception as e:
                print(f"6. ❌ GPU computation test: FAILED - {e}")
                return False
                
            # Check NVIDIA driver
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("7. ✅ NVIDIA driver: Working")
                else:
                    print("7. ⚠️  NVIDIA driver: Check installation")
            except:
                print("7. ❌ nvidia-smi not found - Check NVIDIA driver")
                
            return True
        else:
            print("❌ No GPU detected!")
            print("\nTo enable GPU training:")
            print("1. Install NVIDIA GPU drivers")
            print("2. Install CUDA toolkit")
            print("3. Install PyTorch with CUDA support:")
            print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            return False

def main():
    """Main training pipeline with GPU verification"""
    print("⚡ ElectroVision AI - Training Pipeline")
    print("=" * 50)
    
    # Initialize trainer
    trainer = ElectricalComponentTrainer()
    
    # Check GPU setup
    gpu_available = trainer.check_gpu_setup()
    
    if not gpu_available:
        print("\n⚠️  No GPU available - training will be slow!")
        response = input("Continue with CPU training? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            print("Training cancelled.")
            return
    
    # Create annotation guidelines
    trainer.create_annotation_guidelines()
    
    # Check if dataset exists
    if not any(trainer.train_dir.glob('*.png')) and not any(trainer.train_dir.glob('*.jpg')):
        print("⚠️ No training images found!")
        print("Please add images to:", trainer.train_dir)
        print("And corresponding labels to:", trainer.train_labels_dir)
        print("Use the annotation guidelines to properly label your data.")
        return
    
    # Check validation data and offer to create split if none exists
    has_validation = trainer.check_validation_data()
    
    if not has_validation:
        print("\n🤔 No validation data found.")
        response = input("Would you like to create a validation split from training data? (y/n): ")
        if response.lower() in ['y', 'yes']:
            trainer.split_training_data_for_validation(0.2)  # 20% for validation
    
    print("\n🎯 Starting training process...")
    
    # Train the model (will automatically handle validation and GPU)
    results = trainer.train_model()
    
    # Validate the model only if we have validation data
    if trainer.check_validation_data():
        trainer.validate_model()
    else:
        print("⚠️  Skipping separate validation (no validation data)")
    
    # Test inference
    trainer.test_inference()

if __name__ == '__main__':
    main()
