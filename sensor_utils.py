#!/usr/bin/env python3
"""
Utility functions for sensor monitoring and data processing
"""

import time
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

class DataQuality(Enum):
    """Data quality indicators."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

@dataclass
class SensorReading:
    """Enhanced sensor reading with quality metrics."""
    value: float
    unit: str
    timestamp: float
    quality: DataQuality = DataQuality.UNKNOWN
    confidence: float = 0.0
    raw_data: Optional[Dict] = None

class SensorDataProcessor:
    """Processes and analyzes sensor data."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.data_history: Dict[str, List[float]] = {}
        self.quality_thresholds = {
            'temperature': {'min': -10, 'max': 100, 'variance_threshold': 5.0},
            'battery': {'min': 0, 'max': 100, 'variance_threshold': 2.0},
            'fan_speed': {'min': 0, 'max': 5000, 'variance_threshold': 100.0},
            'voltage': {'min': 0, 'max': 20, 'variance_threshold': 0.5},
            'ambient_light': {'min': 0, 'max': 10000, 'variance_threshold': 100.0},
            'accelerometer': {'min': -50, 'max': 50, 'variance_threshold': 2.0},
            'gyroscope': {'min': -10, 'max': 10, 'variance_threshold': 0.5},
            'lid_angle': {'min': 0, 'max': 360, 'variance_threshold': 5.0}
        }
    
    def add_reading(self, sensor_name: str, value: float) -> SensorReading:
        """Add a new sensor reading and return processed data."""
        if sensor_name not in self.data_history:
            self.data_history[sensor_name] = []
        
        # Add to history
        self.data_history[sensor_name].append(value)
        
        # Maintain window size
        if len(self.data_history[sensor_name]) > self.window_size:
            self.data_history[sensor_name].pop(0)
        
        # Calculate quality metrics
        quality = self._assess_quality(sensor_name, value)
        confidence = self._calculate_confidence(sensor_name, value)
        
        return SensorReading(
            value=value,
            unit=self._get_unit(sensor_name),
            timestamp=time.time(),
            quality=quality,
            confidence=confidence
        )
    
    def _assess_quality(self, sensor_name: str, value: float) -> DataQuality:
        """Assess the quality of a sensor reading."""
        if sensor_name not in self.quality_thresholds:
            return DataQuality.UNKNOWN
        
        thresholds = self.quality_thresholds[sensor_name]
        
        # Check if value is within expected range
        if not (thresholds['min'] <= value <= thresholds['max']):
            return DataQuality.POOR
        
        # Check variance if we have enough data
        if len(self.data_history[sensor_name]) >= 3:
            variance = statistics.variance(self.data_history[sensor_name])
            if variance > thresholds['variance_threshold']:
                return DataQuality.POOR
            elif variance > thresholds['variance_threshold'] * 0.5:
                return DataQuality.FAIR
            else:
                return DataQuality.GOOD
        
        return DataQuality.GOOD
    
    def _calculate_confidence(self, sensor_name: str, value: float) -> float:
        """Calculate confidence score for a sensor reading."""
        if len(self.data_history[sensor_name]) < 2:
            return 0.5
        
        # Calculate how close the value is to recent average
        recent_values = self.data_history[sensor_name][-5:]  # Last 5 readings
        avg_value = statistics.mean(recent_values)
        std_dev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
        
        if std_dev == 0:
            return 1.0
        
        # Calculate z-score
        z_score = abs(value - avg_value) / std_dev
        
        # Convert z-score to confidence (lower z-score = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 - (z_score / 3.0)))
        
        return confidence
    
    def _get_unit(self, sensor_name: str) -> str:
        """Get the unit for a sensor type."""
        units = {
            'temperature': '°C',
            'battery': '%',
            'fan_speed': 'RPM',
            'voltage': 'V',
            'ambient_light': 'lux',
            'accelerometer': 'm/s²',
            'gyroscope': 'rad/s',
            'lid_angle': '°'
        }
        return units.get(sensor_name, '')
    
    def get_statistics(self, sensor_name: str) -> Optional[Dict]:
        """Get statistics for a sensor."""
        if sensor_name not in self.data_history or len(self.data_history[sensor_name]) < 2:
            return None
        
        values = self.data_history[sensor_name]
        
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values),
            'min': min(values),
            'max': max(values),
            'count': len(values),
            'trend': self._calculate_trend(values)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for sensor values."""
        if len(values) < 3:
            return "stable"
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def detect_anomalies(self, sensor_name: str, threshold: float = 2.0) -> List[Tuple[int, float]]:
        """Detect anomalous readings using z-score method."""
        if sensor_name not in self.data_history or len(self.data_history[sensor_name]) < 3:
            return []
        
        values = self.data_history[sensor_name]
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs(value - mean_val) / std_val
            if z_score > threshold:
                anomalies.append((i, value))
        
        return anomalies
    
    def smooth_data(self, sensor_name: str, alpha: float = 0.3) -> List[float]:
        """Apply exponential smoothing to sensor data."""
        if sensor_name not in self.data_history or len(self.data_history[sensor_name]) < 2:
            return []
        
        values = self.data_history[sensor_name]
        smoothed = [values[0]]
        
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
            smoothed.append(smoothed_value)
        
        return smoothed

class SensorAlerts:
    """Manages sensor alerts and notifications."""
    
    def __init__(self):
        self.alerts: Dict[str, List[Dict]] = {}
        self.alert_callbacks = []
    
    def add_alert(self, sensor_name: str, condition: str, threshold: float, 
                  message: str, severity: str = "warning"):
        """Add an alert condition for a sensor."""
        if sensor_name not in self.alerts:
            self.alerts[sensor_name] = []
        
        alert = {
            'condition': condition,
            'threshold': threshold,
            'message': message,
            'severity': severity,
            'active': True
        }
        
        self.alerts[sensor_name].append(alert)
    
    def check_alerts(self, sensor_name: str, value: float) -> List[Dict]:
        """Check if any alerts should be triggered."""
        triggered_alerts = []
        
        if sensor_name not in self.alerts:
            return triggered_alerts
        
        for alert in self.alerts[sensor_name]:
            if not alert['active']:
                continue
            
            condition = alert['condition']
            threshold = alert['threshold']
            triggered = False
            
            if condition == 'greater_than' and value > threshold:
                triggered = True
            elif condition == 'less_than' and value < threshold:
                triggered = True
            elif condition == 'equals' and abs(value - threshold) < 0.01:
                triggered = True
            
            if triggered:
                alert_data = {
                    'sensor': sensor_name,
                    'value': value,
                    'threshold': threshold,
                    'message': alert['message'],
                    'severity': alert['severity'],
                    'timestamp': time.time()
                }
                triggered_alerts.append(alert_data)
                
                # Notify callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert_data)
                    except Exception as e:
                        print(f"Error in alert callback: {e}")
        
        return triggered_alerts
    
    def register_callback(self, callback):
        """Register a callback for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def disable_alert(self, sensor_name: str, alert_index: int):
        """Disable a specific alert."""
        if sensor_name in self.alerts and 0 <= alert_index < len(self.alerts[sensor_name]):
            self.alerts[sensor_name][alert_index]['active'] = False
    
    def enable_alert(self, sensor_name: str, alert_index: int):
        """Enable a specific alert."""
        if sensor_name in self.alerts and 0 <= alert_index < len(self.alerts[sensor_name]):
            self.alerts[sensor_name][alert_index]['active'] = True

class DataExporter:
    """Exports sensor data to various formats."""
    
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str) -> bool:
        """Export sensor data to CSV format."""
        try:
            import csv
            
            if not data:
                return False
            
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_json(data: List[Dict], filename: str) -> bool:
        """Export sensor data to JSON format."""
        try:
            import json
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def export_to_xml(data: List[Dict], filename: str) -> bool:
        """Export sensor data to XML format."""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.Element("sensor_data")
            
            for item in data:
                reading = ET.SubElement(root, "reading")
                for key, value in item.items():
                    elem = ET.SubElement(reading, key)
                    elem.text = str(value)
            
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            
            return True
        except Exception as e:
            print(f"Error exporting to XML: {e}")
            return False