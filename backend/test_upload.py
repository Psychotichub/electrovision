#!/usr/bin/env python3
"""
Test script to debug upload and analysis issues
"""

import requests
import sys
import os
from pathlib import Path

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get('http://localhost:3000/', timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def test_upload_endpoint():
    """Test upload endpoint without file"""
    try:
        response = requests.post('http://localhost:3000/upload', timeout=5)
        print(f"📤 Upload endpoint test: {response.status_code}")
        print(f"📋 Response: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload endpoint error: {e}")
        return False

def create_test_pdf():
    """Create a simple test PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "test_electrical_plan.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add some test content
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Electrical Plan - Test Document")
        c.drawString(100, 720, "Switch: Kitchen light switch")
        c.drawString(100, 690, "Outlet: 120V GFCI outlet")
        c.drawString(100, 660, "Light: LED ceiling fixture")
        c.drawString(100, 630, "Panel: Main electrical panel")
        c.drawString(100, 600, "Wire: 12 AWG copper wire")
        
        c.save()
        print(f"✅ Created test PDF: {filename}")
        return filename
    
    except ImportError:
        print("⚠️ reportlab not available - creating simple text file instead")
        filename = "test_plan.txt"
        with open(filename, 'w') as f:
            f.write("Electrical Plan - Test Document\n")
            f.write("Switch: Kitchen light switch\n")
            f.write("Outlet: 120V GFCI outlet\n")
            f.write("Light: LED ceiling fixture\n")
        return filename

def test_python_script_directly():
    """Test the Python parsing script directly"""
    print("\n🔍 Testing Python script directly...")
    
    # Try to run the PDF parser
    import subprocess
    
    try:
        result = subprocess.run([
            'python', 'python/parse_pdf.py'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(f"📋 Exit code: {result.returncode}")
        print(f"📤 stdout: {result.stdout}")
        print(f"📋 stderr: {result.stderr}")
        
        return result.returncode == 1  # Expected for no file argument
        
    except Exception as e:
        print(f"❌ Script test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ElectroVision AI - Backend Test Suite")
    print("="*50)
    
    # Test 1: Backend health
    print("\n1️⃣ Testing backend health...")
    if not test_backend_health():
        print("💡 Start backend with: cd backend && npm start")
        return
    
    # Test 2: Upload endpoint
    print("\n2️⃣ Testing upload endpoint...")
    test_upload_endpoint()
    
    # Test 3: Python script
    print("\n3️⃣ Testing Python script...")
    test_python_script_directly()
    
    print("\n🎯 Manual Test Instructions:")
    print("1. Upload a PDF file through the web interface")
    print("2. Check backend terminal for detailed error logs")
    print("3. Look for specific error messages in the server output")
    
    print("\n📋 Common Issues:")
    print("• File path problems - check uploads directory")
    print("• Python dependencies - ensure all modules installed")
    print("• File format issues - try different PDF files")
    print("• Timeout errors - large files may need more time")

if __name__ == "__main__":
    main() 