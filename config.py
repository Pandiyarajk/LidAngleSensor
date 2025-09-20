#!/usr/bin/env python3
"""
Configuration management for Lenovo Sensor Monitor
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class SensorConfig:
    """Configuration for individual sensors."""
    enabled: bool = True
    update_interval: float = 1.0
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

@dataclass
class MultimediaConfig:
    """Configuration for multimedia controls."""
    volume_step: int = 5
    enable_hotkeys: bool = True
    show_notifications: bool = True

@dataclass
class UIConfig:
    """Configuration for user interface."""
    window_width: int = 800
    window_height: int = 600
    theme: str = "default"
    auto_refresh: bool = True
    refresh_interval: float = 1.0

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    max_log_size: int = 1024 * 1024  # 1MB
    backup_count: int = 5
    log_to_file: bool = True
    log_to_gui: bool = True

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "sensors": {
                "lid_angle": asdict(SensorConfig()),
                "accelerometer": asdict(SensorConfig()),
                "gyroscope": asdict(SensorConfig()),
                "ambient_light": asdict(SensorConfig()),
                "temperature": asdict(SensorConfig(threshold_warning=70.0, threshold_critical=85.0)),
                "battery": asdict(SensorConfig(threshold_warning=20.0, threshold_critical=10.0)),
                "fan_speed": asdict(SensorConfig()),
                "voltage": asdict(SensorConfig())
            },
            "multimedia": asdict(MultimediaConfig()),
            "ui": asdict(UIConfig()),
            "logging": asdict(LoggingConfig()),
            "general": {
                "start_monitoring_on_startup": False,
                "minimize_to_tray": True,
                "check_for_updates": True
            }
        }
    
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._merge_config(loaded_config)
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
        return False
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _merge_config(self, loaded_config: Dict[str, Any]):
        """Merge loaded configuration with default config."""
        def merge_dicts(default: dict, loaded: dict) -> dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.config = merge_dicts(self.config, loaded_config)
    
    def get_sensor_config(self, sensor_name: str) -> SensorConfig:
        """Get configuration for a specific sensor."""
        sensor_data = self.config.get("sensors", {}).get(sensor_name, {})
        return SensorConfig(**sensor_data)
    
    def set_sensor_config(self, sensor_name: str, config: SensorConfig):
        """Set configuration for a specific sensor."""
        if "sensors" not in self.config:
            self.config["sensors"] = {}
        self.config["sensors"][sensor_name] = asdict(config)
    
    def get_multimedia_config(self) -> MultimediaConfig:
        """Get multimedia configuration."""
        multimedia_data = self.config.get("multimedia", {})
        return MultimediaConfig(**multimedia_data)
    
    def set_multimedia_config(self, config: MultimediaConfig):
        """Set multimedia configuration."""
        self.config["multimedia"] = asdict(config)
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration."""
        ui_data = self.config.get("ui", {})
        return UIConfig(**ui_data)
    
    def set_ui_config(self, config: UIConfig):
        """Set UI configuration."""
        self.config["ui"] = asdict(config)
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        logging_data = self.config.get("logging", {})
        return LoggingConfig(**logging_data)
    
    def set_logging_config(self, config: LoggingConfig):
        """Set logging configuration."""
        self.config["logging"] = asdict(config)
    
    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration."""
        return self.config.get("general", {})
    
    def set_general_config(self, key: str, value: Any):
        """Set general configuration value."""
        if "general" not in self.config:
            self.config["general"] = {}
        self.config["general"][key] = value
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._load_default_config()
    
    def export_config(self, filename: str) -> bool:
        """Export configuration to a file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filename: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(filename, 'r') as f:
                loaded_config = json.load(f)
                self._merge_config(loaded_config)
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False