# Lenovo Laptop Sensor Monitor - Usage Guide

## Quick Start

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python lenovo_sensor_monitor.py
# OR
python run.py
```

### 2. Windows Service Installation (Optional)
```bash
# Install as Windows service
python windows_service.py install

# Start the service
python windows_service.py start

# Stop the service
python windows_service.py stop

# Uninstall the service
python windows_service.py uninstall
```

## Features Overview

### Sensor Monitoring
- **Real-time Data**: Live monitoring of hardware sensors
- **Multiple Sensor Types**: Temperature, battery, fan speed, accelerometer, etc.
- **Data Quality Assessment**: Automatic quality scoring for sensor readings
- **Alert System**: Configurable alerts for critical values
- **Data Export**: Export sensor data to CSV, JSON, or XML

### Multimedia Control
- **Volume Control**: Increase, decrease, and mute system volume
- **Media Playback**: Play/pause, next/previous track, stop
- **Real-time Volume Display**: Current volume level monitoring
- **Hotkey Support**: System-wide media key functionality

### User Interface
- **Modern GUI**: Clean, intuitive interface with tabs
- **Real-time Updates**: Live sensor data visualization
- **Configurable Settings**: Customize monitoring intervals and sensors
- **Logging System**: Comprehensive logging with GUI display
- **Data Export**: Save sensor data in multiple formats

## Detailed Usage

### Sensor Monitor Tab

#### Starting Monitoring
1. Click "Refresh Sensors" to detect available hardware sensors
2. Click "Start Monitoring" to begin real-time data collection
3. View live sensor data in the text area
4. Click "Stop Monitoring" to pause data collection

#### Sensor Data Display
- **Format**: `[timestamp] sensor_name: value unit (status)`
- **Example**: `[14:30:25] temperature: 45.2 °C (active)`
- **Status Indicators**: active, warning, critical, error

#### Available Sensors
- **Lid Angle**: Laptop lid position and angle
- **Accelerometer**: Device orientation and movement
- **Gyroscope**: Rotational motion detection
- **Ambient Light**: Lighting condition monitoring
- **Temperature**: CPU, GPU, and system temperatures
- **Battery**: Battery level and charging status
- **Fan Speed**: Cooling fan speed monitoring
- **Voltage**: System voltage levels

### Multimedia Control Tab

#### Volume Control
- **Volume Up**: Increase system volume
- **Volume Down**: Decrease system volume
- **Mute**: Toggle system mute
- **Volume Display**: Shows current volume percentage

#### Media Control
- **Play/Pause**: Toggle media playback
- **Next Track**: Skip to next media track
- **Previous Track**: Go to previous media track
- **Stop**: Stop media playback

### Settings Tab

#### Monitoring Settings
- **Update Interval**: Set monitoring frequency (default: 1 second)
- **Sensor Selection**: Enable/disable specific sensors
- **Thresholds**: Set warning and critical thresholds

#### Configuration Management
- **Save Settings**: Save current configuration
- **Load Settings**: Load saved configuration
- **Reset to Defaults**: Restore default settings

### Log Tab

#### Log Management
- **View Logs**: Real-time log display
- **Clear Log**: Clear the log display
- **Save Log**: Export logs to file
- **Log Levels**: INFO, WARNING, ERROR, DEBUG

## Advanced Usage

### Configuration Files

#### config.json
Main configuration file with sensor settings, thresholds, and preferences.

```json
{
  "sensors": {
    "temperature": {
      "enabled": true,
      "update_interval": 1.0,
      "threshold_warning": 70.0,
      "threshold_critical": 85.0
    }
  },
  "multimedia": {
    "volume_step": 5,
    "enable_hotkeys": true,
    "show_notifications": true
  }
}
```

### Command Line Usage

#### Direct Module Execution
```bash
# Run main application
python -m lenovo_sensor_monitor

# Run test suite
python test_sensors.py

# Run examples
python example_usage.py
```

#### Windows Service Commands
```bash
# Install service
python windows_service.py install

# Start service
python windows_service.py start

# Stop service
python windows_service.py stop

# Restart service
python windows_service.py restart

# Uninstall service
python windows_service.py uninstall
```

### API Usage

#### Basic Sensor Monitoring
```python
from lenovo_sensor_monitor import SensorMonitor, SensorType

# Initialize monitor
monitor = SensorMonitor()
monitor.initialize_wmi()

# Detect sensors
available = monitor.detect_sensors()
print(f"Available sensors: {available}")

# Read sensor data
data = monitor.read_sensor_data(SensorType.TEMPERATURE)
if data:
    print(f"Temperature: {data.value} {data.unit}")
```

#### Multimedia Control
```python
from lenovo_sensor_monitor import MultimediaController

# Initialize controller
controller = MultimediaController()

# Control volume
controller.volume_up()
controller.volume_down()
controller.toggle_mute()

# Control media
controller.play_pause()
controller.next_track()
controller.previous_track()
controller.stop_media()

# Get current volume
volume = controller.get_volume_level()
print(f"Current volume: {volume}%")
```

#### Advanced Data Processing
```python
from sensor_utils import SensorDataProcessor, SensorAlerts

# Data processor
processor = SensorDataProcessor()

# Add readings
reading = processor.add_reading('temperature', 45.0)
print(f"Quality: {reading.quality}, Confidence: {reading.confidence}")

# Get statistics
stats = processor.get_statistics('temperature')
print(f"Mean: {stats['mean']}, Trend: {stats['trend']}")

# Alert system
alerts = SensorAlerts()
alerts.add_alert('temperature', 'greater_than', 80.0, 
                'High temperature!', 'warning')
```

## Troubleshooting

### Common Issues

#### 1. Sensors Not Detected
**Symptoms**: No sensors appear in the sensor list
**Solutions**:
- Ensure Lenovo Vantage is installed and updated
- Check Windows Device Manager for sensor drivers
- Run application as administrator
- Verify WMI service is running

#### 2. Multimedia Controls Not Working
**Symptoms**: Volume/media buttons don't respond
**Solutions**:
- Check audio drivers are installed and updated
- Verify Windows audio service is running
- Ensure no other application is blocking media keys
- Try running as administrator

#### 3. Permission Errors
**Symptoms**: Access denied or permission errors
**Solutions**:
- Run application as administrator
- Check Windows User Account Control settings
- Verify COM+ services are enabled
- Check Windows Firewall settings

#### 4. WMI Connection Errors
**Symptoms**: WMI initialization fails
**Solutions**:
- Ensure Windows Management Instrumentation service is running
- Check Windows Firewall settings
- Verify COM+ services are enabled
- Restart Windows Management Instrumentation service

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

- **Application Log**: `sensor_monitor.log`
- **Service Log**: `lenovo_sensor_service.log`
- **Configuration**: `config.json`
- **Settings**: `settings.json`

## Performance Tips

### Optimization
- Increase monitoring interval for better performance
- Disable unused sensors
- Use data smoothing for noisy sensors
- Set appropriate thresholds to reduce false alerts

### Resource Usage
- Typical CPU usage: 1-3%
- Memory usage: 50-100 MB
- Disk usage: < 10 MB (excluding logs)
- Network usage: Minimal (WMI queries only)

## Security Considerations

### Permissions
- Application requires administrator privileges for full functionality
- WMI access requires appropriate permissions
- Media control requires audio device access

### Data Privacy
- No data is transmitted over the network
- All data remains on local system
- Logs may contain system information

## Support and Development

### Getting Help
1. Check this usage guide
2. Review application logs
3. Run the test suite: `python test_sensors.py`
4. Check Windows Event Viewer for system errors

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Reporting Issues
When reporting issues, please include:
- Windows version and build
- Lenovo laptop model
- Python version
- Application logs
- Steps to reproduce the issue