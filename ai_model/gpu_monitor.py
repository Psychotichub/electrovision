#!/usr/bin/env python3
"""
GPU Monitor for ElectroVision AI Training
Run this script in a separate terminal while training to monitor GPU usage
"""

import torch
import time
import os
import sys
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_gpu_info():
    """Get comprehensive GPU information"""
    if not torch.cuda.is_available():
        return None
    
    gpu_info = {}
    gpu_info['name'] = torch.cuda.get_device_name(0)
    gpu_info['count'] = torch.cuda.device_count()
    
    # Memory info
    gpu_info['memory_total'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    gpu_info['memory_allocated'] = torch.cuda.memory_allocated(0) / (1024**3)
    gpu_info['memory_cached'] = torch.cuda.memory_reserved(0) / (1024**3)
    gpu_info['memory_free'] = gpu_info['memory_total'] - gpu_info['memory_allocated']
    
    # Usage percentages
    gpu_info['memory_usage_percent'] = (gpu_info['memory_allocated'] / gpu_info['memory_total']) * 100
    gpu_info['cache_usage_percent'] = (gpu_info['memory_cached'] / gpu_info['memory_total']) * 100
    
    return gpu_info

def display_gpu_status():
    """Display real-time GPU status"""
    gpu_info = get_gpu_info()
    
    if gpu_info is None:
        print("❌ No CUDA GPUs detected!")
        return False
    
    print("🔥 GPU REAL-TIME MONITOR")
    print("=" * 60)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🚀 GPU: {gpu_info['name']}")
    print(f"📊 Device Count: {gpu_info['count']}")
    print("")
    
    # Memory information
    print("💾 MEMORY USAGE:")
    print(f"   Total:     {gpu_info['memory_total']:.1f} GB")
    print(f"   Allocated: {gpu_info['memory_allocated']:.2f} GB ({gpu_info['memory_usage_percent']:.1f}%)")
    print(f"   Cached:    {gpu_info['memory_cached']:.2f} GB ({gpu_info['cache_usage_percent']:.1f}%)")
    print(f"   Free:      {gpu_info['memory_free']:.2f} GB")
    print("")
    
    # Visual memory bar
    bar_length = 40
    allocated_bars = int((gpu_info['memory_usage_percent'] / 100) * bar_length)
    cached_bars = int((gpu_info['cache_usage_percent'] / 100) * bar_length)
    
    print("📊 MEMORY VISUALIZATION:")
    print(f"   Allocated: [{'█' * allocated_bars}{'░' * (bar_length - allocated_bars)}] {gpu_info['memory_usage_percent']:.1f}%")
    print(f"   Cached:    [{'█' * cached_bars}{'░' * (bar_length - cached_bars)}] {gpu_info['cache_usage_percent']:.1f}%")
    print("")
    
    # Status indicators
    if gpu_info['memory_usage_percent'] < 50:
        status = "🟢 LOW USAGE"
    elif gpu_info['memory_usage_percent'] < 80:
        status = "🟡 MODERATE USAGE"
    else:
        status = "🔴 HIGH USAGE"
    
    print(f"🎯 Status: {status}")
    print("=" * 60)
    print("Press Ctrl+C to exit monitor")
    
    return True

def main():
    """Main monitoring loop"""
    print("🚀 ElectroVision AI - GPU Monitor")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        print("❌ No CUDA GPUs available to monitor!")
        sys.exit(1)
    
    print("🔄 Starting GPU monitoring...")
    print("   Refresh rate: 2 seconds")
    print("   Press Ctrl+C to stop")
    print("")
    
    try:
        while True:
            clear_screen()
            display_gpu_status()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 GPU monitoring stopped.")
        print("Thank you for using ElectroVision AI GPU Monitor!")

if __name__ == "__main__":
    main() 