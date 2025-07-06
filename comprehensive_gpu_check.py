#!/usr/bin/env python3
"""
Comprehensive GPU Detection Script
Checks for all types of GPUs and provides detailed system information
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_pytorch_gpu():
    """Check PyTorch GPU availability"""
    print("\n" + "="*60)
    print("PYTORCH GPU DETECTION")
    print("="*60)
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✓ CUDA version: {torch.version.cuda}")
            print(f"✓ Number of CUDA GPUs: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                device_name = torch.cuda.get_device_name(i)
                memory_gb = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"  GPU {i}: {device_name} ({memory_gb:.1f} GB)")
                
            # Current GPU
            current_device = torch.cuda.current_device()
            print(f"✓ Current CUDA device: {current_device}")
            
            # Test GPU computation
            try:
                x = torch.rand(1000, 1000).cuda()
                y = torch.rand(1000, 1000).cuda()
                z = torch.matmul(x, y)
                print("✓ GPU computation test: PASSED")
            except Exception as e:
                print(f"✗ GPU computation test: FAILED - {e}")
        else:
            print("✗ No CUDA GPUs detected by PyTorch")
            
    except ImportError:
        print("✗ PyTorch not installed")
    except Exception as e:
        print(f"✗ Error checking PyTorch: {e}")

def check_system_gpus():
    """Check system GPUs using various methods"""
    print("\n" + "="*60)
    print("SYSTEM GPU DETECTION")
    print("="*60)
    
    # Check using wmic (Windows)
    if platform.system() == "Windows":
        print("\n--- Windows GPU Detection ---")
        
        # Get GPU info using wmic
        cmd = 'wmic path win32_videocontroller get name,adapterram,driverversion /format:csv'
        stdout, stderr, returncode = run_command(cmd)
        
        if returncode == 0 and stdout:
            lines = stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip() and 'Node' not in line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            name = parts[2].strip()
                            ram = parts[1].strip()
                            driver = parts[3].strip()
                            if name and name != 'Name':
                                print(f"✓ GPU: {name}")
                                if ram and ram != 'AdapterRAM':
                                    try:
                                        ram_gb = int(ram) / (1024**3)
                                        print(f"  Memory: {ram_gb:.1f} GB")
                                    except:
                                        print(f"  Memory: {ram}")
                                if driver and driver != 'DriverVersion':
                                    print(f"  Driver: {driver}")
                        except:
                            continue
        
        # Check DirectX info
        print("\n--- DirectX GPU Information ---")
        cmd = 'dxdiag /t dxdiag_output.txt'
        stdout, stderr, returncode = run_command(cmd)
        
        if os.path.exists('dxdiag_output.txt'):
            try:
                with open('dxdiag_output.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract GPU info
                lines = content.split('\n')
                gpu_section = False
                for line in lines:
                    if 'Card name:' in line:
                        gpu_name = line.split('Card name:')[1].strip()
                        print(f"✓ DirectX GPU: {gpu_name}")
                    elif 'Display Memory:' in line:
                        memory = line.split('Display Memory:')[1].strip()
                        print(f"  Display Memory: {memory}")
                
                # Clean up
                os.remove('dxdiag_output.txt')
            except Exception as e:
                print(f"✗ Error reading DirectX info: {e}")

def check_nvidia_gpus():
    """Check NVIDIA GPUs using nvidia-smi"""
    print("\n" + "="*60)
    print("NVIDIA GPU DETECTION")
    print("="*60)
    
    # Check nvidia-smi
    stdout, stderr, returncode = run_command('nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader,nounits')
    
    if returncode == 0 and stdout:
        print("✓ NVIDIA GPU(s) detected:")
        lines = stdout.strip().split('\n')
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                name, memory, driver = parts[0], parts[1], parts[2]
                compute_cap = parts[3] if len(parts) > 3 else "Unknown"
                print(f"  GPU {i}: {name}")
                print(f"    Memory: {memory} MB")
                print(f"    Driver: {driver}")
                print(f"    Compute Capability: {compute_cap}")
    else:
        print("✗ No NVIDIA GPUs detected (nvidia-smi not available)")
        if stderr:
            print(f"  Error: {stderr}")

def check_opencl():
    """Check OpenCL GPUs"""
    print("\n" + "="*60)
    print("OPENCL GPU DETECTION")
    print("="*60)
    
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        
        if platforms:
            print("✓ OpenCL platforms detected:")
            for platform in platforms:
                print(f"  Platform: {platform.name}")
                devices = platform.get_devices()
                for device in devices:
                    print(f"    Device: {device.name}")
                    print(f"    Type: {cl.device_type.to_string(device.type)}")
                    print(f"    Max Compute Units: {device.max_compute_units}")
                    print(f"    Global Memory: {device.global_mem_size / (1024**3):.1f} GB")
        else:
            print("✗ No OpenCL platforms detected")
            
    except ImportError:
        print("✗ PyOpenCL not installed")
    except Exception as e:
        print(f"✗ Error checking OpenCL: {e}")

def check_tensorflow_gpu():
    """Check TensorFlow GPU availability"""
    print("\n" + "="*60)
    print("TENSORFLOW GPU DETECTION")
    print("="*60)
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow version: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✓ TensorFlow GPUs detected: {len(gpus)}")
            for i, gpu in enumerate(gpus):
                print(f"  GPU {i}: {gpu.name}")
                
            # Check GPU details
            gpu_details = tf.config.experimental.get_device_details(gpus[0])
            if gpu_details:
                print(f"  Compute Capability: {gpu_details.get('compute_capability', 'Unknown')}")
        else:
            print("✗ No GPUs detected by TensorFlow")
            
    except ImportError:
        print("✗ TensorFlow not installed")
    except Exception as e:
        print(f"✗ Error checking TensorFlow: {e}")

def main():
    """Main function to run all GPU checks"""
    print("=" * 80)
    print("COMPREHENSIVE GPU DETECTION REPORT")
    print("=" * 80)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Architecture: {platform.architecture()[0]}")
    
    # Run all checks
    check_pytorch_gpu()
    check_system_gpus()
    check_nvidia_gpus()
    check_opencl()
    check_tensorflow_gpu()
    
    print("\n" + "="*80)
    print("GPU DETECTION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main() 