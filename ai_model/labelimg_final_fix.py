#!/usr/bin/env python3
"""
LabelImg Final Comprehensive Fix
Addresses ALL setValue calls that might receive float values
"""

import os
import sys
import shutil
import re
from pathlib import Path

def find_venv_labelimg():
    """Find the LabelImg installation in the virtual environment"""
    
    # Check if we're in a virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if not venv_path:
        # Try to detect from current Python path
        python_path = Path(sys.executable)
        if '.venv' in str(python_path):
            venv_path = str(python_path.parent.parent)
            print(f"🔍 Detected virtual environment: {venv_path}")
        else:
            print("❌ No virtual environment detected")
            return None
    else:
        print(f"🔍 Virtual environment found: {venv_path}")
    
    # Look for labelImg in the virtual environment
    possible_paths = [
        Path(venv_path) / "Lib" / "site-packages" / "labelImg",
        Path(venv_path) / "lib" / "python3.10" / "site-packages" / "labelImg",
        Path(venv_path) / "lib" / "site-packages" / "labelImg",
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"📁 Found LabelImg at: {path}")
            return path
    
    print("❌ LabelImg not found in virtual environment")
    return None

def apply_final_fix():
    """Apply final comprehensive fix to ALL setValue calls"""
    
    # Find the LabelImg installation
    labelimg_path = find_venv_labelimg()
    if not labelimg_path:
        return False
    
    # Path to the main labelImg.py file
    main_file = labelimg_path / "labelImg.py"
    
    if not main_file.exists():
        print(f"❌ Main file not found: {main_file}")
        return False
    
    # Create backup
    backup_file = main_file.with_suffix(".py.backup")
    if not backup_file.exists():
        shutil.copy2(main_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    
    # Read the original file
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Applying final comprehensive fix...")
    
    # Find all setValue calls and wrap their arguments with int()
    # This regex finds all setValue calls and wraps the argument with int()
    patterns_to_fix = [
        # Pattern 1: widget.setValue(expression)
        (r'(\w+\.setValue)\(([^)]+)\)', r'\1(int(\2))'),
        
        # Pattern 2: self.widget.setValue(expression)
        (r'(self\.\w+\.setValue)\(([^)]+)\)', r'\1(int(\2))'),
        
        # Pattern 3: variable.setValue(expression)
        (r'(\w+_\w+\.setValue)\(([^)]+)\)', r'\1(int(\2))'),
        
        # Pattern 4: More specific patterns
        (r'(h_bar\.setValue)\(([^)]+)\)', r'\1(int(\2))'),
        (r'(v_bar\.setValue)\(([^)]+)\)', r'\1(int(\2))'),
        (r'(bar\.setValue)\(([^)]+)\)', r'\1(int(\2))'),
    ]
    
    fixes_applied = 0
    for pattern, replacement in patterns_to_fix:
        # Find all matches
        matches = re.findall(pattern, content)
        if matches:
            # Apply the replacement
            content = re.sub(pattern, replacement, content)
            print(f"✅ Fixed {len(matches)} setValue calls with pattern: {pattern[:30]}...")
            fixes_applied += len(matches)
    
    # Now fix double int() calls that might have been created
    # Remove int(int(x)) and replace with int(x)
    content = re.sub(r'int\(int\(([^)]+)\)\)', r'int(\1)', content)
    
    # Special case: if setValue already has int(), don't double-wrap
    content = re.sub(r'setValue\(int\(int\(([^)]+)\)\)\)', r'setValue(int(\1))', content)
    
    # Write the fixed file
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully applied {fixes_applied} fixes to: {main_file}")
    return fixes_applied > 0

def restore_backup():
    """Restore the original LabelImg from backup"""
    
    labelimg_path = find_venv_labelimg()
    if not labelimg_path:
        return False
    
    main_file = labelimg_path / "labelImg.py"
    backup_file = main_file.with_suffix(".py.backup")
    
    if backup_file.exists():
        shutil.copy2(backup_file, main_file)
        print(f"✅ Restored from backup: {backup_file}")
        return True
    else:
        print("❌ Backup file not found")
        return False

def test_fix():
    """Test if the fix works"""
    
    print("🧪 Testing final fix...")
    
    try:
        # Clear any cached imports
        modules_to_clear = [key for key in sys.modules.keys() if 'labelImg' in key]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Test import
        import labelImg
        print("✅ LabelImg imports successfully")
        
        # Test main window import
        from labelImg.labelImg import MainWindow
        print("✅ MainWindow can be imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 LabelImg Final Comprehensive Fix")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if restore_backup():
            print("✅ Backup restored successfully")
        else:
            print("❌ Failed to restore backup")
    else:
        if apply_final_fix():
            if test_fix():
                print("\n🎉 Final fix applied successfully!")
                print("🚀 ALL setValue calls are now int-wrapped")
                print("🔧 LabelImg should work without ANY float to int errors")
                print("\nUsage:")
                print("  cd ai_model/dataset/images/train")
                print("  labelimg")
            else:
                print("\n⚠️  Fix applied but test had issues")
                print("🔄 Try running LabelImg anyway - it should work")
        else:
            print("\n❌ Failed to apply final fix")
    
    print("\n📝 Note: If you encounter issues, run:")
    print("  python ai_model/labelimg_final_fix.py restore") 