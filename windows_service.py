#!/usr/bin/env python3
"""
Windows Service wrapper for Lenovo Sensor Monitor
"""

import sys
import os
import time
import logging
import threading
from typing import Optional

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False

from lenovo_sensor_monitor import SensorMonitor, MultimediaController

class LenovoSensorService:
    """Windows Service for Lenovo Sensor Monitor."""
    
    def __init__(self):
        self.sensor_monitor = SensorMonitor()
        self.multimedia_controller = MultimediaController()
        self.running = False
        self.monitor_thread = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('lenovo_sensor_service.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Start sensor monitoring in background thread."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Sensor monitoring started")
    
    def stop_monitoring(self):
        """Stop sensor monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Sensor monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            # Initialize WMI
            if not self.sensor_monitor.initialize_wmi():
                self.logger.error("Failed to initialize WMI")
                return
            
            # Detect sensors
            available_sensors = self.sensor_monitor.detect_sensors()
            self.logger.info(f"Detected sensors: {available_sensors}")
            
            # Start monitoring
            self.sensor_monitor.start_monitoring(interval=1.0)
            
            # Keep running until stopped
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
        finally:
            self.sensor_monitor.stop_monitoring()

if WINDOWS_SERVICE_AVAILABLE:
    class LenovoSensorWindowsService(win32serviceutil.ServiceFramework):
        """Windows Service implementation."""
        
        _svc_name_ = "LenovoSensorMonitor"
        _svc_display_name_ = "Lenovo Laptop Sensor Monitor"
        _svc_description_ = "Monitors hardware sensors and provides multimedia control for Lenovo laptops"
        
        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.service = LenovoSensorService()
        
        def SvcStop(self):
            """Stop the service."""
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.service.stop_monitoring()
            win32event.SetEvent(self.hWaitStop)
        
        def SvcDoRun(self):
            """Run the service."""
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                servicemanager.PYS_SERVICE_STARTED,
                                (self._svc_name_, ''))
            
            try:
                self.service.start_monitoring()
                
                # Wait for stop event
                win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
                
            except Exception as e:
                servicemanager.LogErrorMsg(f"Service error: {e}")
            finally:
                self.service.stop_monitoring()

def install_service():
    """Install the Windows service."""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Windows service modules not available. Install pywin32 package.")
        return False
    
    try:
        win32serviceutil.InstallService(
            LenovoSensorWindowsService._svc_reg_class_,
            LenovoSensorWindowsService._svc_name_,
            LenovoSensorWindowsService._svc_display_name_,
            description=LenovoSensorWindowsService._svc_description_
        )
        print("Service installed successfully")
        return True
    except Exception as e:
        print(f"Error installing service: {e}")
        return False

def uninstall_service():
    """Uninstall the Windows service."""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Windows service modules not available.")
        return False
    
    try:
        win32serviceutil.RemoveService(LenovoSensorWindowsService._svc_name_)
        print("Service uninstalled successfully")
        return True
    except Exception as e:
        print(f"Error uninstalling service: {e}")
        return False

def start_service():
    """Start the Windows service."""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Windows service modules not available.")
        return False
    
    try:
        win32serviceutil.StartService(LenovoSensorWindowsService._svc_name_)
        print("Service started successfully")
        return True
    except Exception as e:
        print(f"Error starting service: {e}")
        return False

def stop_service():
    """Stop the Windows service."""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Windows service modules not available.")
        return False
    
    try:
        win32serviceutil.StopService(LenovoSensorWindowsService._svc_name_)
        print("Service stopped successfully")
        return True
    except Exception as e:
        print(f"Error stopping service: {e}")
        return False

def main():
    """Main entry point for service management."""
    if len(sys.argv) == 1:
        # Run as service
        if WINDOWS_SERVICE_AVAILABLE:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(LenovoSensorWindowsService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("Windows service modules not available. Running in console mode.")
            service = LenovoSensorService()
            try:
                service.start_monitoring()
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                service.stop_monitoring()
    else:
        # Handle command line arguments
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'uninstall':
            uninstall_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'restart':
            stop_service()
            time.sleep(2)
            start_service()
        else:
            print("Usage: python windows_service.py [install|uninstall|start|stop|restart]")

if __name__ == '__main__':
    main()