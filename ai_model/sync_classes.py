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
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False
    
    # Extract class names
    if 'names' not in config:
        print("❌ No 'names' section found in config.yaml")
        return False
    
    names = config['names']
    nc = config.get('nc', len(names))
    
    print(f"📋 Found {nc} classes in config.yaml")
    
    # Create classes content - ensure consecutive numbering from 0
    classes_content = []
    missing_classes = []
    
    for i in range(nc):
        if i in names:
            class_name = names[i]
            # Skip reserved classes in the output
            if not class_name.startswith('reserved_'):
                classes_content.append(class_name)
            else:
                classes_content.append(class_name)  # Keep reserved for consistency
        else:
            missing_classes.append(i)
            classes_content.append(f"missing_class_{i}")
    
    if missing_classes:
        print(f"⚠️  Warning: Missing classes at indices: {missing_classes}")
    
    # Remove any reserved classes from final output if needed
    # For now, keep all classes to maintain index consistency
    classes_text = '\n'.join(classes_content) + '\n'
    
    # Define target locations - only where actually needed
    target_files = [
        "classes.txt",                           # Master copy in ai_model/
        "dataset/classes.txt",                   # Dataset copy for annotation tools
    ]
    
    # Write classes.txt files
    success_count = 0
    for target_file in target_files:
        target_path = Path(target_file)
        
        # Create directory if it doesn't exist
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️  Could not create directory for {target_file}: {e}")
            continue
        
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
        start_idx = max(0, len(classes_content) - 10)
        for i, class_name in enumerate(classes_content[-10:], start_idx):
            print(f"   {i}: {class_name}")
    
    # Show class categories summary
    print("\n📈 Class Categories Summary:")
    categories = {
        'Protection & Safety': list(range(8)),
        'Control & Switching': list(range(8, 15)),
        'Wiring & Connection': list(range(15, 23)),
        'Lighting': list(range(23, 31)),
        'Power & Connection': list(range(31, 35)),
        'Earthing & Grounding': list(range(35, 41)),
        'Measurement': list(range(41, 50)),
        'Power Equipment': list(range(50, 57)),
        'Sensors & Detection': list(range(57, 62)),
        'Alarm & Signaling': list(range(62, 67)),
        'Access & Control': list(range(67, 69)),
        'Documentation': list(range(69, 71)),
        'Reserved': list(range(71, nc))
    }
    
    for category, indices in categories.items():
        count = len([i for i in indices if i < len(classes_content)])
        if count > 0:
            print(f"   {category}: {count} classes")
    
    return success_count == len(target_files)

def validate_sync():
    """Validate that all classes.txt files match config.yaml"""
    
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found!")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False
    
    names = config['names']
    nc = config.get('nc', len(names))
    
    # Build expected classes list
    expected_classes = []
    for i in range(nc):
        if i in names:
            expected_classes.append(names[i])
        else:
            expected_classes.append(f"missing_class_{i}")
    
    target_files = [
        "classes.txt",
        "dataset/classes.txt", 
    ]
    
    all_match = True
    synced_files = 0
    
    for target_file in target_files:
        target_path = Path(target_file)
        if target_path.exists():
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    actual_classes = [line.strip() for line in f.readlines() if line.strip()]
                
                if actual_classes == expected_classes:
                    print(f"✅ {target_file}: In sync ({len(actual_classes)} classes)")
                    synced_files += 1
                else:
                    print(f"❌ {target_file}: Out of sync (expected {len(expected_classes)}, got {len(actual_classes)})")
                    all_match = False
            except Exception as e:
                print(f"❌ {target_file}: Error reading file - {e}")
                all_match = False
        else:
            print(f"❌ {target_file}: Missing")
            all_match = False
    
    print(f"\n📊 Validation Summary: {synced_files}/{len(target_files)} files are in sync")
    return all_match

def show_class_mapping():
    """Show the current class mapping from config.yaml"""
    
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found!")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False
    
    names = config['names']
    nc = config.get('nc', len(names))
    
    print(f"\n📋 Current Class Mapping ({nc} classes):")
    print("=" * 60)
    
    for i in range(nc):
        if i in names:
            class_name = names[i]
            status = "🟢" if not class_name.startswith('reserved_') else "🔵"
            print(f"{status} {i:2d}: {class_name}")
        else:
            print(f"🔴 {i:2d}: MISSING")
    
    return True

if __name__ == "__main__":
    print("🔄 Class Definition Sync Tool")
    print("=" * 50)
    
    # Show current mapping
    show_class_mapping()
    
    print("\n🔄 Syncing classes...")
    if sync_classes():
        print("\n🎉 All classes.txt files are now in sync with config.yaml!")
    else:
        print("\n❌ Some files could not be synced. Check the errors above.")
    
    print("\n🔍 Validation:")
    if validate_sync():
        print("✅ All files are in sync!")
    else:
        print("❌ Some files are out of sync!")
    
    print("\n💡 Use this tool whenever you modify class definitions in config.yaml")
    print("📁 Classes will be synced to all training directories automatically") 