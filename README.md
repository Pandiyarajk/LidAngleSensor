# Lenovo Laptop Sensor Monitor & Multimedia Control

A comprehensive Python application for monitoring hardware sensors and controlling multimedia on Lenovo laptops running Windows OS.

## Features

### Sensor Monitoring
- **Lid Angle Sensor**: Monitor laptop lid position and angle
- **Accelerometer**: Track device orientation and movement
- **Gyroscope**: Monitor rotational motion
- **Ambient Light Sensor**: Track lighting conditions
- **Temperature Sensors**: Monitor CPU, GPU, and system temperatures
- **Battery Monitoring**: Track battery level and charging status
- **Fan Speed Monitoring**: Monitor cooling fan speeds
- **Voltage Monitoring**: Track system voltage levels

### Multimedia Control
- **Volume Control**: Increase, decrease, and mute system volume
- **Media Playback**: Play/pause, next/previous track, stop media
- **Real-time Volume Display**: Show current volume level
- **Media Status Monitoring**: Track media playback status

### User Interface
- **Modern GUI**: Clean, intuitive interface using tkinter
- **Real-time Monitoring**: Live sensor data updates
- **Configurable Settings**: Customize monitoring intervals and sensor selection
- **Logging System**: Comprehensive logging with GUI display
- **Multi-tab Interface**: Organized tabs for different functionalities

## Requirements

- Windows 10/11 (64-bit)
- Python 3.8 or higher
- Lenovo laptop with compatible sensors
- Administrator privileges (for some sensor access)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd lenovo-sensor-monitor
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python lenovo_sensor_monitor.py
   ```

## Usage

### Starting the Application
1. Run `python lenovo_sensor_monitor.py`
2. The application will automatically detect available sensors
3. Click "Refresh Sensors" to update the sensor list

### Sensor Monitoring
1. Go to the "Sensor Monitor" tab
2. Click "Start Monitoring" to begin real-time sensor data collection
3. View live sensor data in the text area
4. Click "Stop Monitoring" to pause data collection

### Multimedia Control
1. Go to the "Multimedia Control" tab
2. Use the volume control buttons to adjust system volume
3. Use media control buttons to control playback
4. Monitor current volume level in the status area

### Settings Configuration
1. Go to the "Settings" tab
2. Adjust monitoring interval (default: 1 second)
3. Enable/disable specific sensors
4. Click "Save Settings" to apply changes

### Logging
1. Go to the "Log" tab to view application logs
2. Use "Clear Log" to clear the display
3. Use "Save Log" to save logs to a file

## Supported Lenovo Models

This application is designed to work with Lenovo laptops that have:
- ThinkPad series (X, T, P, E, L series)
- IdeaPad series
- Yoga series
- Legion series

### Sensor Compatibility
- **Lid Angle**: Most modern Lenovo laptops
- **Accelerometer/Gyroscope**: Yoga series, some ThinkPad models
- **Ambient Light**: Most models with adaptive brightness
- **Temperature**: All models (via WMI/ACPI)
- **Battery**: All models
- **Fan Speed**: All models with active cooling

## Technical Details

### Architecture
- **Sensor Monitor**: Handles hardware sensor detection and data collection
- **Multimedia Controller**: Manages system volume and media controls
- **GUI Application**: Provides user interface and data visualization
- **WMI Integration**: Accesses Windows Management Instrumentation for hardware data

### APIs Used
- **Windows Sensor API**: For hardware sensor access
- **WMI (Windows Management Instrumentation)**: For system information
- **Windows Multimedia API**: For volume and media control
- **psutil**: For system monitoring and hardware information

### Data Sources
- **WMI Queries**: System hardware information
- **psutil**: Process and system monitoring
- **Windows Registry**: System configuration
- **ACPI Tables**: Hardware sensor data

## Troubleshooting

### Common Issues

1. **Sensors not detected**
   - Ensure Lenovo Vantage is installed and updated
   - Check Windows Device Manager for sensor drivers
   - Run application as administrator

2. **Multimedia controls not working**
   - Verify audio drivers are installed and updated
   - Check Windows audio service is running
   - Ensure no other application is blocking media keys

3. **Permission errors**
   - Run application as administrator
   - Check Windows User Account Control settings

4. **WMI connection errors**
   - Ensure Windows Management Instrumentation service is running
   - Check Windows Firewall settings
   - Verify COM+ services are enabled

### Debug Mode
Enable debug logging by modifying the logging level in the code:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided as-is for educational and personal use. The authors are not responsible for any damage to hardware or software. Use at your own risk.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the application logs
3. Create an issue on the project repository
4. Contact Lenovo support for hardware-specific issues

## Changelog

### Version 1.0.0
- Initial release
- Basic sensor monitoring functionality
- Multimedia control features
- GUI interface
- WMI integration
- Logging system