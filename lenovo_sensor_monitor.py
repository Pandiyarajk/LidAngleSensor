#!/usr/bin/env python3
"""
Lenovo Laptop Sensor Monitor and Multimedia Control
A comprehensive tool for monitoring sensors and controlling multimedia on Lenovo laptops running Windows.
"""

import sys
import os
import time
import threading
import json
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ctypes
from ctypes import wintypes, windll, byref, c_ulong, c_void_p, c_char_p
import subprocess
import psutil
import wmi

# Windows API constants
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2

# Windows API functions
user32 = windll.user32
kernel32 = windll.kernel32
ole32 = windll.ole32

# Initialize COM
ole32.CoInitialize(None)

class SensorType(Enum):
    """Types of sensors that can be monitored."""
    LID_ANGLE = "lid_angle"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    AMBIENT_LIGHT = "ambient_light"
    TEMPERATURE = "temperature"
    BATTERY = "battery"
    FAN_SPEED = "fan_speed"
    VOLTAGE = "voltage"

@dataclass
class SensorData:
    """Data structure for sensor readings."""
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: float
    status: str = "active"

class MultimediaController:
    """Handles multimedia control functionality."""
    
    def __init__(self):
        self.volume_level = 0
        self.is_muted = False
        
    def send_key(self, vk_code: int):
        """Send a virtual key press."""
        try:
            # Key down
            user32.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)  # Small delay
            # Key up
            user32.keybd_event(vk_code, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
            return True
        except Exception as e:
            logging.error(f"Failed to send key {vk_code}: {e}")
            return False
    
    def volume_up(self):
        """Increase system volume."""
        return self.send_key(VK_VOLUME_UP)
    
    def volume_down(self):
        """Decrease system volume."""
        return self.send_key(VK_VOLUME_DOWN)
    
    def toggle_mute(self):
        """Toggle system mute."""
        return self.send_key(VK_VOLUME_MUTE)
    
    def play_pause(self):
        """Toggle media play/pause."""
        return self.send_key(VK_MEDIA_PLAY_PAUSE)
    
    def next_track(self):
        """Skip to next media track."""
        return self.send_key(VK_MEDIA_NEXT_TRACK)
    
    def previous_track(self):
        """Go to previous media track."""
        return self.send_key(VK_MEDIA_PREV_TRACK)
    
    def stop_media(self):
        """Stop media playback."""
        return self.send_key(VK_MEDIA_STOP)
    
    def get_volume_level(self) -> int:
        """Get current system volume level."""
        try:
            # Use PowerShell to get volume level
            cmd = "powershell -Command \"[audio]::Volume * 100\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                volume_str = result.stdout.strip()
                if volume_str:
                    return int(float(volume_str))
        except Exception as e:
            logging.error(f"Failed to get volume level: {e}")
        return 0

class SensorMonitor:
    """Monitors various hardware sensors on Lenovo laptops."""
    
    def __init__(self):
        self.sensors = {}
        self.wmi_conn = None
        self.running = False
        self.callbacks = {}
        
    def initialize_wmi(self):
        """Initialize WMI connection."""
        try:
            self.wmi_conn = wmi.WMI()
            logging.info("WMI connection initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize WMI: {e}")
            return False
    
    def detect_sensors(self) -> Dict[str, bool]:
        """Detect available sensors on the system."""
        available_sensors = {}
        
        if not self.wmi_conn:
            if not self.initialize_wmi():
                return available_sensors
        
        try:
            # Check for sensor devices in WMI
            sensor_devices = self.wmi_conn.Win32_PnPEntity()
            
            for device in sensor_devices:
                device_name = device.Name or ""
                device_class = device.DeviceClass or ""
                
                # Check for accelerometer
                if any(keyword in device_name.lower() for keyword in ['accelerometer', 'accel', 'motion']):
                    available_sensors[SensorType.ACCELEROMETER.value] = True
                
                # Check for gyroscope
                if any(keyword in device_name.lower() for keyword in ['gyroscope', 'gyro', 'rotation']):
                    available_sensors[SensorType.GYROSCOPE.value] = True
                
                # Check for ambient light sensor
                if any(keyword in device_name.lower() for keyword in ['light', 'ambient', 'brightness']):
                    available_sensors[SensorType.AMBIENT_LIGHT.value] = True
                
                # Check for temperature sensors
                if any(keyword in device_name.lower() for keyword in ['temperature', 'thermal', 'temp']):
                    available_sensors[SensorType.TEMPERATURE.value] = True
            
            # Check for battery
            try:
                battery = psutil.sensors_battery()
                if battery:
                    available_sensors[SensorType.BATTERY.value] = True
            except:
                pass
            
            # Check for temperature sensors using psutil
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    available_sensors[SensorType.TEMPERATURE.value] = True
            except:
                pass
            
            # Check for fan sensors
            try:
                fans = psutil.sensors_fans()
                if fans:
                    available_sensors[SensorType.FAN_SPEED.value] = True
            except:
                pass
            
            # Lid angle sensor is typically handled by ACPI/WMI
            available_sensors[SensorType.LID_ANGLE.value] = self._check_lid_sensor()
            
        except Exception as e:
            logging.error(f"Error detecting sensors: {e}")
        
        return available_sensors
    
    def _check_lid_sensor(self) -> bool:
        """Check if lid angle sensor is available."""
        try:
            # Check for lid switch in WMI
            lid_switches = self.wmi_conn.Win32_SystemEnclosure()
            for enclosure in lid_switches:
                if hasattr(enclosure, 'ChassisTypes'):
                    # Chassis type 10 is laptop
                    if 10 in enclosure.ChassisTypes:
                        return True
        except Exception as e:
            logging.error(f"Error checking lid sensor: {e}")
        return False
    
    def read_sensor_data(self, sensor_type: SensorType) -> Optional[SensorData]:
        """Read data from a specific sensor."""
        try:
            if sensor_type == SensorType.BATTERY:
                return self._read_battery_data()
            elif sensor_type == SensorType.TEMPERATURE:
                return self._read_temperature_data()
            elif sensor_type == SensorType.FAN_SPEED:
                return self._read_fan_data()
            elif sensor_type == SensorType.LID_ANGLE:
                return self._read_lid_angle_data()
            elif sensor_type == SensorType.AMBIENT_LIGHT:
                return self._read_ambient_light_data()
            elif sensor_type == SensorType.ACCELEROMETER:
                return self._read_accelerometer_data()
            elif sensor_type == SensorType.GYROSCOPE:
                return self._read_gyroscope_data()
        except Exception as e:
            logging.error(f"Error reading {sensor_type.value} sensor: {e}")
        return None
    
    def _read_battery_data(self) -> Optional[SensorData]:
        """Read battery sensor data."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return SensorData(
                    sensor_type=SensorType.BATTERY,
                    value=battery.percent,
                    unit="%",
                    timestamp=time.time(),
                    status="charging" if battery.power_plugged else "discharging"
                )
        except Exception as e:
            logging.error(f"Error reading battery data: {e}")
        return None
    
    def _read_temperature_data(self) -> Optional[SensorData]:
        """Read temperature sensor data."""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get the first available temperature sensor
                for name, entries in temps.items():
                    if entries:
                        return SensorData(
                            sensor_type=SensorType.TEMPERATURE,
                            value=entries[0].current,
                            unit="°C",
                            timestamp=time.time()
                        )
        except Exception as e:
            logging.error(f"Error reading temperature data: {e}")
        return None
    
    def _read_fan_data(self) -> Optional[SensorData]:
        """Read fan speed sensor data."""
        try:
            fans = psutil.sensors_fans()
            if fans:
                # Get the first available fan sensor
                for name, entries in fans.items():
                    if entries:
                        return SensorData(
                            sensor_type=SensorType.FAN_SPEED,
                            value=entries[0].current,
                            unit="RPM",
                            timestamp=time.time()
                        )
        except Exception as e:
            logging.error(f"Error reading fan data: {e}")
        return None
    
    def _read_lid_angle_data(self) -> Optional[SensorData]:
        """Read lid angle sensor data."""
        try:
            # This is a simplified implementation
            # In reality, lid angle detection would require specific Lenovo drivers/APIs
            # For now, we'll simulate based on system power state
            battery = psutil.sensors_battery()
            if battery and not battery.power_plugged:
                # Simulate lid angle based on power state
                # This is not accurate but demonstrates the concept
                return SensorData(
                    sensor_type=SensorType.LID_ANGLE,
                    value=90.0,  # Simulated angle
                    unit="degrees",
                    timestamp=time.time()
                )
        except Exception as e:
            logging.error(f"Error reading lid angle data: {e}")
        return None
    
    def _read_ambient_light_data(self) -> Optional[SensorData]:
        """Read ambient light sensor data."""
        try:
            # This would require specific Lenovo sensor drivers
            # For demonstration, we'll return a simulated value
            return SensorData(
                sensor_type=SensorType.AMBIENT_LIGHT,
                value=500.0,  # Simulated lux value
                unit="lux",
                timestamp=time.time()
            )
        except Exception as e:
            logging.error(f"Error reading ambient light data: {e}")
        return None
    
    def _read_accelerometer_data(self) -> Optional[SensorData]:
        """Read accelerometer sensor data."""
        try:
            # This would require specific Lenovo sensor drivers
            # For demonstration, we'll return simulated values
            return SensorData(
                sensor_type=SensorType.ACCELEROMETER,
                value=9.8,  # Simulated acceleration
                unit="m/s²",
                timestamp=time.time()
            )
        except Exception as e:
            logging.error(f"Error reading accelerometer data: {e}")
        return None
    
    def _read_gyroscope_data(self) -> Optional[SensorData]:
        """Read gyroscope sensor data."""
        try:
            # This would require specific Lenovo sensor drivers
            # For demonstration, we'll return simulated values
            return SensorData(
                sensor_type=SensorType.GYROSCOPE,
                value=0.0,  # Simulated angular velocity
                unit="rad/s",
                timestamp=time.time()
            )
        except Exception as e:
            logging.error(f"Error reading gyroscope data: {e}")
        return None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start monitoring sensors at specified interval."""
        self.running = True
        
        def monitor_loop():
            while self.running:
                try:
                    for sensor_type in SensorType:
                        data = self.read_sensor_data(sensor_type)
                        if data:
                            self.sensors[sensor_type.value] = data
                            
                            # Call registered callbacks
                            if sensor_type.value in self.callbacks:
                                for callback in self.callbacks[sensor_type.value]:
                                    try:
                                        callback(data)
                                    except Exception as e:
                                        logging.error(f"Error in sensor callback: {e}")
                except Exception as e:
                    logging.error(f"Error in monitoring loop: {e}")
                
                time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logging.info("Sensor monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring sensors."""
        self.running = False
        logging.info("Sensor monitoring stopped")
    
    def register_callback(self, sensor_type: SensorType, callback: Callable[[SensorData], None]):
        """Register a callback for sensor data updates."""
        if sensor_type.value not in self.callbacks:
            self.callbacks[sensor_type.value] = []
        self.callbacks[sensor_type.value].append(callback)

class LenovoSensorMonitorApp:
    """Main GUI application for Lenovo sensor monitoring."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lenovo Laptop Sensor Monitor & Multimedia Control")
        self.root.geometry("800x600")
        
        # Initialize components
        self.sensor_monitor = SensorMonitor()
        self.multimedia_controller = MultimediaController()
        
        # Available sensors
        self.available_sensors = {}
        self.sensor_data = {}
        
        # Setup GUI
        self.setup_gui()
        
        # Initialize monitoring
        self.initialize_monitoring()
        
        # Start periodic volume updates
        self.update_volume_periodically()
    
    def setup_gui(self):
        """Setup the GUI components."""
        # Create main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sensor monitoring tab
        self.setup_sensor_tab(notebook)
        
        # Multimedia control tab
        self.setup_multimedia_tab(notebook)
        
        # Settings tab
        self.setup_settings_tab(notebook)
        
        # Log tab
        self.setup_log_tab(notebook)
    
    def setup_sensor_tab(self, notebook):
        """Setup the sensor monitoring tab."""
        sensor_frame = ttk.Frame(notebook)
        notebook.add(sensor_frame, text="Sensor Monitor")
        
        # Sensor status frame
        status_frame = ttk.LabelFrame(sensor_frame, text="Sensor Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Available sensors list
        self.sensor_listbox = tk.Listbox(status_frame, height=8)
        self.sensor_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Refresh button
        refresh_btn = ttk.Button(status_frame, text="Refresh Sensors", command=self.refresh_sensors)
        refresh_btn.pack(pady=5)
        
        # Sensor data frame
        data_frame = ttk.LabelFrame(sensor_frame, text="Sensor Data")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sensor data display
        self.sensor_data_text = scrolledtext.ScrolledText(data_frame, height=15)
        self.sensor_data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(sensor_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_multimedia_tab(self, notebook):
        """Setup the multimedia control tab."""
        media_frame = ttk.Frame(notebook)
        notebook.add(media_frame, text="Multimedia Control")
        
        # Volume control frame
        volume_frame = ttk.LabelFrame(media_frame, text="Volume Control")
        volume_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Volume buttons
        vol_btn_frame = ttk.Frame(volume_frame)
        vol_btn_frame.pack(pady=10)
        
        ttk.Button(vol_btn_frame, text="Volume Up", command=self.multimedia_controller.volume_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(vol_btn_frame, text="Volume Down", command=self.multimedia_controller.volume_down).pack(side=tk.LEFT, padx=5)
        ttk.Button(vol_btn_frame, text="Mute", command=self.multimedia_controller.toggle_mute).pack(side=tk.LEFT, padx=5)
        
        # Volume level display
        self.volume_label = ttk.Label(volume_frame, text="Volume: 0%")
        self.volume_label.pack(pady=5)
        
        # Media control frame
        media_control_frame = ttk.LabelFrame(media_frame, text="Media Control")
        media_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Media buttons
        media_btn_frame = ttk.Frame(media_control_frame)
        media_btn_frame.pack(pady=10)
        
        ttk.Button(media_btn_frame, text="Play/Pause", command=self.multimedia_controller.play_pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(media_btn_frame, text="Next Track", command=self.multimedia_controller.next_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(media_btn_frame, text="Previous Track", command=self.multimedia_controller.previous_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(media_btn_frame, text="Stop", command=self.multimedia_controller.stop_media).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(media_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.media_status_text = scrolledtext.ScrolledText(status_frame, height=10)
        self.media_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_settings_tab(self, notebook):
        """Setup the settings tab."""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Monitoring settings
        monitor_frame = ttk.LabelFrame(settings_frame, text="Monitoring Settings")
        monitor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(monitor_frame, text="Update Interval (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.interval_var = tk.StringVar(value="1.0")
        interval_entry = ttk.Entry(monitor_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Sensor selection
        sensor_frame = ttk.LabelFrame(settings_frame, text="Sensor Selection")
        sensor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.sensor_vars = {}
        for sensor_type in SensorType:
            var = tk.BooleanVar(value=True)
            self.sensor_vars[sensor_type.value] = var
            ttk.Checkbutton(sensor_frame, text=sensor_type.value.replace('_', ' ').title(), 
                          variable=var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Save settings button
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
    
    def setup_log_tab(self, notebook):
        """Setup the log tab."""
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log control buttons
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_btn_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
    
    def initialize_monitoring(self):
        """Initialize sensor monitoring."""
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Add log handler for GUI
        log_handler = LogHandler(self.log_text)
        logging.getLogger().addHandler(log_handler)
        
        # Detect available sensors
        self.refresh_sensors()
        
        # Register sensor callbacks
        for sensor_type in SensorType:
            self.sensor_monitor.register_callback(sensor_type, self.on_sensor_data_update)
    
    def refresh_sensors(self):
        """Refresh the list of available sensors."""
        self.available_sensors = self.sensor_monitor.detect_sensors()
        
        # Update sensor listbox
        self.sensor_listbox.delete(0, tk.END)
        for sensor_name, available in self.available_sensors.items():
            status = "Available" if available else "Not Available"
            self.sensor_listbox.insert(tk.END, f"{sensor_name}: {status}")
        
        logging.info(f"Detected {sum(self.available_sensors.values())} available sensors")
    
    def start_monitoring(self):
        """Start sensor monitoring."""
        try:
            interval = float(self.interval_var.get())
            self.sensor_monitor.start_monitoring(interval)
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            logging.info("Sensor monitoring started")
        except ValueError:
            messagebox.showerror("Error", "Invalid interval value")
    
    def stop_monitoring(self):
        """Stop sensor monitoring."""
        self.sensor_monitor.stop_monitoring()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        logging.info("Sensor monitoring stopped")
    
    def on_sensor_data_update(self, data: SensorData):
        """Handle sensor data updates."""
        self.sensor_data[data.sensor_type.value] = data
        
        # Schedule GUI updates on main thread
        self.root.after(0, self.update_sensor_display)
        
        # Update volume display for battery sensor
        if data.sensor_type == SensorType.BATTERY:
            self.root.after(0, self.update_volume_display)
    
    def update_sensor_display(self):
        """Update the sensor data display."""
        self.sensor_data_text.delete(1.0, tk.END)
        
        for sensor_name, data in self.sensor_data.items():
            if data:
                timestamp = time.strftime("%H:%M:%S", time.localtime(data.timestamp))
                self.sensor_data_text.insert(tk.END, 
                    f"[{timestamp}] {sensor_name}: {data.value:.2f} {data.unit} ({data.status})\n")
    
    def update_volume_display(self):
        """Update the volume display."""
        volume = self.multimedia_controller.get_volume_level()
        self.volume_label.config(text=f"Volume: {volume}%")
    
    def update_volume_periodically(self):
        """Update volume display periodically."""
        self.update_volume_display()
        # Update every 2 seconds
        self.root.after(2000, self.update_volume_periodically)
    
    def save_settings(self):
        """Save application settings."""
        settings = {
            "interval": self.interval_var.get(),
            "enabled_sensors": {name: var.get() for name, var in self.sensor_vars.items()}
        }
        
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            logging.info("Settings saved")
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def clear_log(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file."""
        try:
            with open("sensor_monitor.log", "w") as f:
                f.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Success", "Log saved to sensor_monitor.log")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

class LogHandler(logging.Handler):
    """Custom log handler for GUI display."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)

def main():
    """Main entry point."""
    if sys.platform != "win32":
        print("This application is designed for Windows OS only.")
        return
    
    try:
        app = LenovoSensorMonitorApp()
        app.run()
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()