#!/usr/bin/env python3
"""
Test script for Lenovo Sensor Monitor
"""

import sys
import time
import logging
from lenovo_sensor_monitor import SensorMonitor, MultimediaController, SensorType

def test_sensor_detection():
    """Test sensor detection functionality."""
    print("Testing sensor detection...")
    
    monitor = SensorMonitor()
    
    # Initialize WMI
    if not monitor.initialize_wmi():
        print("❌ Failed to initialize WMI")
        return False
    
    # Detect sensors
    available_sensors = monitor.detect_sensors()
    print(f"Available sensors: {available_sensors}")
    
    if not available_sensors:
        print("❌ No sensors detected")
        return False
    
    print("✅ Sensor detection test passed")
    return True

def test_sensor_reading():
    """Test sensor data reading."""
    print("Testing sensor data reading...")
    
    monitor = SensorMonitor()
    monitor.initialize_wmi()
    
    # Test reading each sensor type
    for sensor_type in SensorType:
        print(f"Testing {sensor_type.value}...")
        data = monitor.read_sensor_data(sensor_type)
        
        if data:
            print(f"  ✅ {sensor_type.value}: {data.value} {data.unit}")
        else:
            print(f"  ⚠️  {sensor_type.value}: No data available")
    
    print("✅ Sensor reading test completed")
    return True

def test_multimedia_control():
    """Test multimedia control functionality."""
    print("Testing multimedia control...")
    
    controller = MultimediaController()
    
    # Test volume control
    print("Testing volume control...")
    try:
        # Get current volume
        current_volume = controller.get_volume_level()
        print(f"Current volume: {current_volume}%")
        
        # Test volume up (be careful not to make it too loud)
        print("Testing volume up...")
        if controller.volume_up():
            print("  ✅ Volume up command sent")
        else:
            print("  ❌ Volume up command failed")
        
        time.sleep(0.5)
        
        # Test volume down
        print("Testing volume down...")
        if controller.volume_down():
            print("  ✅ Volume down command sent")
        else:
            print("  ❌ Volume down command failed")
        
        time.sleep(0.5)
        
        # Test mute toggle
        print("Testing mute toggle...")
        if controller.toggle_mute():
            print("  ✅ Mute toggle command sent")
        else:
            print("  ❌ Mute toggle command failed")
        
        time.sleep(0.5)
        
        # Test media controls
        print("Testing media controls...")
        if controller.play_pause():
            print("  ✅ Play/pause command sent")
        else:
            print("  ❌ Play/pause command failed")
        
        print("✅ Multimedia control test completed")
        return True
        
    except Exception as e:
        print(f"❌ Multimedia control test failed: {e}")
        return False

def test_monitoring_loop():
    """Test sensor monitoring loop."""
    print("Testing sensor monitoring loop...")
    
    monitor = SensorMonitor()
    monitor.initialize_wmi()
    
    # Register callback
    def on_data_update(data):
        print(f"  📊 {data.sensor_type.value}: {data.value} {data.unit}")
    
    for sensor_type in SensorType:
        monitor.register_callback(sensor_type, on_data_update)
    
    # Start monitoring for 5 seconds
    print("Starting 5-second monitoring test...")
    monitor.start_monitoring(interval=1.0)
    
    time.sleep(5)
    
    monitor.stop_monitoring()
    print("✅ Monitoring loop test completed")
    return True

def run_all_tests():
    """Run all tests."""
    print("Lenovo Sensor Monitor - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Sensor Detection", test_sensor_detection),
        ("Sensor Reading", test_sensor_reading),
        ("Multimedia Control", test_multimedia_control),
        ("Monitoring Loop", test_monitoring_loop)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def main():
    """Main test function."""
    if sys.platform != "win32":
        print("❌ This test suite is designed for Windows OS only.")
        return False
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        return run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)