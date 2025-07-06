#!/usr/bin/env python3
"""
Sync class definitions from config.yaml to classes.txt files
This ensures config.yaml is the single source of truth for class definitions
"""

import yaml
import os
from pathlib import Path

def sync_classes():
    """Sync classes from config.yaml to classes.txt files"""
    
    # Load config.yaml
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found!")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Extract class names
    if 'names' not in config:
        print("❌ No 'names' section found in config.yaml")
        return False
    
    names = config['names']
    nc = config.get('nc', len(names))
    
    print(f"📋 Found {nc} classes in config.yaml")
    
    # Create classes content
    classes_content = []
    for i in range(nc):
        if i in names:
            classes_content.append(names[i])
        else:
            print(f"⚠️  Warning: Class {i} not found in names")
    
    classes_text = '\n'.join(classes_content) + '\n'
    
    # Define target locations (updated for actual project structure)
    target_files = [
        "classes.txt",                           # Master copy in ai_model/
        "dataset/classes.txt",                   # Dataset copy  
        "dataset/images/train/classes.txt",      # LabelImg train directory
        "dataset/images/val/classes.txt",        # LabelImg val directory
        "dataset/labels/train/classes.txt",      # Label files train directory
        "dataset/labels/val/classes.txt",        # Label files val directory
    ]
    
    # Write classes.txt files
    success_count = 0
    for target_file in target_files:
        target_path = Path(target_file)
        
        # Create directory if it doesn't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(classes_text)
            print(f"✅ Updated: {target_file}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to update {target_file}: {e}")
    
    print(f"\n🎯 Successfully updated {success_count}/{len(target_files)} files")
    print(f"📊 Classes synced: {len(classes_content)} classes")
    
    # Show first 10 classes and last 10 classes for verification
    print("\n📋 First 10 Classes:")
    for i, class_name in enumerate(classes_content[:10]):
        print(f"   {i}: {class_name}")
    
    if len(classes_content) > 10:
        print("\n📋 Last 10 Classes:")
        for i, class_name in enumerate(classes_content[-10:], len(classes_content) - 10):
            print(f"   {i}: {class_name}")
    
    return success_count == len(target_files)

def validate_sync():
    """Validate that all classes.txt files match config.yaml"""
    
    config_path = Path("config.yaml")
    if not config_path.exists():
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    names = config['names']
    expected_classes = [names[i] for i in range(len(names))]
    
    target_files = [
        "classes.txt",
        "dataset/classes.txt", 
        "dataset/images/train/classes.txt",
        "dataset/images/val/classes.txt",
        "dataset/labels/train/classes.txt",
        "dataset/labels/val/classes.txt",
    ]
    
    all_match = True
    for target_file in target_files:
        target_path = Path(target_file)
        if target_path.exists():
            with open(target_path, 'r', encoding='utf-8') as f:
                actual_classes = [line.strip() for line in f.readlines() if line.strip()]
            
            if actual_classes == expected_classes:
                print(f"✅ {target_file}: In sync")
            else:
                print(f"❌ {target_file}: Out of sync ({len(actual_classes)} vs {len(expected_classes)} classes)")
                all_match = False
        else:
            print(f"❌ {target_file}: Missing")
            all_match = False
    
    return all_match

if __name__ == "__main__":
    print("🔄 Class Definition Sync Tool")
    print("=" * 40)
    
    if sync_classes():
        print("\n🎉 All classes.txt files are now in sync with config.yaml!")
    else:
        print("\n❌ Some files could not be synced. Check the errors above.")
    
    print("\n🔍 Validation:")
    if validate_sync():
        print("✅ All files are in sync!")
    else:
        print("❌ Some files are out of sync!") 