#!/usr/bin/env python3
"""
Simple launcher script for Lenovo Sensor Monitor
"""

import sys
import os
import subprocess

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['psutil', 'WMI', 'win32api']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("Lenovo Laptop Sensor Monitor")
    print("=" * 30)
    
    # Check if running on Windows
    if sys.platform != "win32":
        print("❌ This application is designed for Windows OS only.")
        input("Press Enter to exit...")
        return
    
    # Check requirements
    if not check_requirements():
        input("Press Enter to exit...")
        return
    
    # Check if main module exists
    if not os.path.exists("lenovo_sensor_monitor.py"):
        print("❌ Main application file not found.")
        print("Please ensure lenovo_sensor_monitor.py is in the same directory.")
        input("Press Enter to exit...")
        return
    
    try:
        # Import and run the main application
        from lenovo_sensor_monitor import main as run_app
        run_app()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()