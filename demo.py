#!/usr/bin/env python3
"""
Demo script for Lenovo Sensor Monitor
Shows key features and capabilities
"""

import time
import sys
from lenovo_sensor_monitor import SensorMonitor, MultimediaController, SensorType

def demo_sensor_detection():
    """Demonstrate sensor detection capabilities."""
    print("🔍 Sensor Detection Demo")
    print("-" * 30)
    
    monitor = SensorMonitor()
    
    if not monitor.initialize_wmi():
        print("❌ Failed to initialize WMI")
        return False
    
    print("✅ WMI initialized successfully")
    
    # Detect available sensors
    available_sensors = monitor.detect_sensors()
    print(f"\n📊 Available sensors:")
    for sensor_name, available in available_sensors.items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"  {sensor_name}: {status}")
    
    return True

def demo_sensor_reading():
    """Demonstrate sensor data reading."""
    print("\n📈 Sensor Data Reading Demo")
    print("-" * 30)
    
    monitor = SensorMonitor()
    monitor.initialize_wmi()
    
    print("Reading sensor data...")
    
    for sensor_type in SensorType:
        data = monitor.read_sensor_data(sensor_type)
        if data:
            print(f"  {sensor_type.value}: {data.value} {data.unit} ({data.status})")
        else:
            print(f"  {sensor_type.value}: No data available")

def demo_multimedia_control():
    """Demonstrate multimedia control capabilities."""
    print("\n🎵 Multimedia Control Demo")
    print("-" * 30)
    
    controller = MultimediaController()
    
    # Get current volume
    current_volume = controller.get_volume_level()
    print(f"Current volume: {current_volume}%")
    
    print("\nAvailable multimedia controls:")
    print("  - Volume Up/Down")
    print("  - Mute Toggle")
    print("  - Play/Pause")
    print("  - Next/Previous Track")
    print("  - Stop Media")
    
    print("\nNote: Multimedia controls are available but not executed in demo mode")
    print("to avoid unexpected volume changes or media playback.")

def demo_monitoring_session():
    """Demonstrate a short monitoring session."""
    print("\n⏱️  Monitoring Session Demo")
    print("-" * 30)
    
    monitor = SensorMonitor()
    monitor.initialize_wmi()
    
    # Callback for data updates
    def on_data_update(data):
        print(f"  📊 {data.sensor_type.value}: {data.value} {data.unit}")
    
    # Register callbacks
    for sensor_type in SensorType:
        monitor.register_callback(sensor_type, on_data_update)
    
    print("Starting 5-second monitoring session...")
    print("(Press Ctrl+C to stop early)")
    
    try:
        monitor.start_monitoring(interval=1.0)
        time.sleep(5)
        monitor.stop_monitoring()
        print("✅ Monitoring session completed")
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n⚠️  Monitoring session interrupted")

def demo_configuration():
    """Demonstrate configuration management."""
    print("\n⚙️  Configuration Demo")
    print("-" * 30)
    
    try:
        from config import ConfigManager
        
        config = ConfigManager()
        
        print("Configuration management features:")
        print("  - Sensor-specific settings")
        print("  - Threshold configuration")
        print("  - Update intervals")
        print("  - Multimedia preferences")
        print("  - UI customization")
        
        # Show some example configurations
        temp_config = config.get_sensor_config('temperature')
        print(f"\nTemperature sensor config:")
        print(f"  Enabled: {temp_config.enabled}")
        print(f"  Update interval: {temp_config.update_interval}s")
        print(f"  Warning threshold: {temp_config.threshold_warning}°C")
        print(f"  Critical threshold: {temp_config.threshold_critical}°C")
        
        print("\n✅ Configuration system working")
        
    except ImportError:
        print("❌ Configuration module not available")

def demo_data_processing():
    """Demonstrate data processing capabilities."""
    print("\n🔄 Data Processing Demo")
    print("-" * 30)
    
    try:
        from sensor_utils import SensorDataProcessor, SensorAlerts
        
        processor = SensorDataProcessor()
        alerts = SensorAlerts()
        
        print("Data processing features:")
        print("  - Quality assessment")
        print("  - Confidence scoring")
        print("  - Statistical analysis")
        print("  - Anomaly detection")
        print("  - Data smoothing")
        print("  - Alert system")
        
        # Add some sample data
        print("\nProcessing sample temperature data...")
        temperatures = [20, 22, 25, 28, 30, 32, 35, 38, 40, 42]
        
        for i, temp in enumerate(temperatures):
            reading = processor.add_reading('temperature', temp)
            print(f"  Reading {i+1}: {temp}°C (Quality: {reading.quality.value})")
        
        # Show statistics
        stats = processor.get_statistics('temperature')
        if stats:
            print(f"\nStatistics:")
            print(f"  Mean: {stats['mean']:.1f}°C")
            print(f"  Min: {stats['min']:.1f}°C")
            print(f"  Max: {stats['max']:.1f}°C")
            print(f"  Trend: {stats['trend']}")
        
        print("\n✅ Data processing system working")
        
    except ImportError:
        print("❌ Data processing modules not available")

def main():
    """Run the complete demo."""
    print("🚀 Lenovo Laptop Sensor Monitor - Demo")
    print("=" * 50)
    
    if sys.platform != "win32":
        print("❌ This demo is designed for Windows OS only.")
        return
    
    demos = [
        ("Sensor Detection", demo_sensor_detection),
        ("Sensor Reading", demo_sensor_reading),
        ("Multimedia Control", demo_multimedia_control),
        ("Configuration", demo_configuration),
        ("Data Processing", demo_data_processing),
        ("Monitoring Session", demo_monitoring_session)
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            demo_func()
        except KeyboardInterrupt:
            print(f"\n⚠️  {demo_name} interrupted by user")
            break
        except Exception as e:
            print(f"❌ {demo_name} failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nTo run the full application:")
    print("  python lenovo_sensor_monitor.py")
    print("  python run.py")

if __name__ == "__main__":
    main()