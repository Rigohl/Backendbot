"""
Configuración simple para BackendBot
"""

import os
import json
from typing import Dict, Any


class Config:
    """Configuración simple basada en archivo JSON"""

    def __init__(self, config_file: str = None):
        if config_file is None:
            # Usar config por defecto
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config')
            config_file = os.path.join(config_dir, 'backendbot.yaml')

        self.config_file = config_file
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.endswith('.yaml'):
                        import yaml
                        return yaml.safe_load(f) or {}
                    elif self.config_file.endswith('.json'):
                        return json.load(f)
            return self._get_default_config()
        except Exception:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'app': {
                'name': 'BackendBot',
                'version': '2.0',
                'debug': False
            },
            'monitoring': {
                'cpu_threshold': 80.0,
                'memory_threshold': 85.0,
                'disk_threshold': 90.0
            },
            'modes': {
                'default': 'relax',
                'available': ['editor', 'streaming', 'relax', 'gaming', 'desarrollo']
            }
        }

    def get(self, key: str, default=None):
        """Obtener valor de configuración"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Establecer valor de configuración"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self):
        """Guardar configuración"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml'):
                    import yaml
                    yaml.dump(self._config, f, default_flow_style=False)
                elif self.config_file.endswith('.json'):
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")


# Instancia global
config = Config()