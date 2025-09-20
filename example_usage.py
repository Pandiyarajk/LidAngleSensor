#!/usr/bin/env python3
"""
Example usage of Lenovo Sensor Monitor components
"""

import time
import logging
from lenovo_sensor_monitor import SensorMonitor, MultimediaController, SensorType
from sensor_utils import SensorDataProcessor, SensorAlerts, DataExporter
from config import ConfigManager

def example_basic_monitoring():
    """Example of basic sensor monitoring."""
    print("=== Basic Sensor Monitoring Example ===")
    
    # Initialize components
    monitor = SensorMonitor()
    multimedia = MultimediaController()
    
    # Initialize WMI
    if not monitor.initialize_wmi():
        print("Failed to initialize WMI")
        return
    
    # Detect available sensors
    available_sensors = monitor.detect_sensors()
    print(f"Available sensors: {available_sensors}")
    
    # Read sensor data once
    print("\nReading sensor data:")
    for sensor_type in SensorType:
        data = monitor.read_sensor_data(sensor_type)
        if data:
            print(f"  {sensor_type.value}: {data.value} {data.unit}")
    
    # Test multimedia controls
    print("\nTesting multimedia controls:")
    print(f"Current volume: {multimedia.get_volume_level()}%")
    
    # Note: Be careful with volume changes in examples
    print("Volume controls available (not executing to avoid loud sounds)")

def example_continuous_monitoring():
    """Example of continuous sensor monitoring with callbacks."""
    print("\n=== Continuous Monitoring Example ===")
    
    monitor = SensorMonitor()
    monitor.initialize_wmi()
    
    # Data processor for enhanced analysis
    processor = SensorDataProcessor()
    
    # Alert system
    alerts = SensorAlerts()
    
    # Add some example alerts
    alerts.add_alert('temperature', 'greater_than', 80.0, 
                    'High temperature detected!', 'warning')
    alerts.add_alert('battery', 'less_than', 20.0, 
                    'Low battery warning!', 'critical')
    
    # Callback for sensor data updates
    def on_sensor_update(data):
        print(f"📊 {data.sensor_type.value}: {data.value} {data.unit}")
        
        # Process data for quality assessment
        reading = processor.add_reading(data.sensor_type.value, data.value)
        print(f"   Quality: {reading.quality.value}, Confidence: {reading.confidence:.2f}")
        
        # Check for alerts
        triggered = alerts.check_alerts(data.sensor_type.value, data.value)
        for alert in triggered:
            print(f"   🚨 ALERT: {alert['message']} (Severity: {alert['severity']})")
    
    # Register callbacks
    for sensor_type in SensorType:
        monitor.register_callback(sensor_type, on_sensor_update)
    
    # Start monitoring
    print("Starting 10-second monitoring session...")
    monitor.start_monitoring(interval=1.0)
    
    time.sleep(10)
    
    monitor.stop_monitoring()
    print("Monitoring session completed")
    
    # Show statistics
    print("\nSensor Statistics:")
    for sensor_name in ['temperature', 'battery', 'fan_speed']:
        stats = processor.get_statistics(sensor_name)
        if stats:
            print(f"  {sensor_name}: mean={stats['mean']:.2f}, trend={stats['trend']}")

def example_configuration_management():
    """Example of configuration management."""
    print("\n=== Configuration Management Example ===")
    
    config = ConfigManager()
    
    # Get sensor configuration
    temp_config = config.get_sensor_config('temperature')
    print(f"Temperature sensor config: {temp_config}")
    
    # Modify configuration
    temp_config.threshold_warning = 75.0
    temp_config.threshold_critical = 90.0
    config.set_sensor_config('temperature', temp_config)
    
    # Save configuration
    if config.save_config():
        print("Configuration saved successfully")
    
    # Load configuration
    if config.load_config():
        print("Configuration loaded successfully")

def example_data_export():
    """Example of data export functionality."""
    print("\n=== Data Export Example ===")
    
    # Generate some sample data
    sample_data = []
    for i in range(10):
        sample_data.append({
            'timestamp': time.time() + i,
            'sensor': 'temperature',
            'value': 50.0 + i * 2,
            'unit': '°C',
            'quality': 'good'
        })
    
    # Export to different formats
    exporter = DataExporter()
    
    if exporter.export_to_csv(sample_data, 'sensor_data.csv'):
        print("✅ Data exported to CSV")
    
    if exporter.export_to_json(sample_data, 'sensor_data.json'):
        print("✅ Data exported to JSON")
    
    if exporter.export_to_xml(sample_data, 'sensor_data.xml'):
        print("✅ Data exported to XML")

def example_advanced_features():
    """Example of advanced sensor features."""
    print("\n=== Advanced Features Example ===")
    
    processor = SensorDataProcessor()
    
    # Simulate some sensor data
    sensor_name = 'temperature'
    values = [20, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55]
    
    print(f"Processing {len(values)} readings for {sensor_name}:")
    
    for i, value in enumerate(values):
        reading = processor.add_reading(sensor_name, value)
        print(f"  Reading {i+1}: {value}°C (Quality: {reading.quality.value}, Confidence: {reading.confidence:.2f})")
    
    # Get statistics
    stats = processor.get_statistics(sensor_name)
    if stats:
        print(f"\nStatistics for {sensor_name}:")
        print(f"  Mean: {stats['mean']:.2f}°C")
        print(f"  Min: {stats['min']:.2f}°C")
        print(f"  Max: {stats['max']:.2f}°C")
        print(f"  Std Dev: {stats['std_dev']:.2f}°C")
        print(f"  Trend: {stats['trend']}")
    
    # Detect anomalies
    anomalies = processor.detect_anomalies(sensor_name, threshold=2.0)
    if anomalies:
        print(f"\nAnomalies detected: {len(anomalies)}")
        for index, value in anomalies:
            print(f"  Index {index}: {value}°C")
    else:
        print("\nNo anomalies detected")
    
    # Apply smoothing
    smoothed = processor.smooth_data(sensor_name, alpha=0.3)
    if smoothed:
        print(f"\nSmoothed data (last 5 values): {smoothed[-5:]}")

def main():
    """Run all examples."""
    print("Lenovo Sensor Monitor - Usage Examples")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Run examples
        example_basic_monitoring()
        example_continuous_monitoring()
        example_configuration_management()
        example_data_export()
        example_advanced_features()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed with exception: {e}")
        logging.exception("Example execution failed")

if __name__ == "__main__":
    main()