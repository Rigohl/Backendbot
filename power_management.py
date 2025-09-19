#!/usr/bin/env python3
"""
Sistema de Gestión de Energía Inteligente - BackendBot
Implementa perfiles de energía adaptativos y optimización automática
"""
import os
import sys
import json
import psutil
import platform
import subprocess
import glob
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.core.di.container import container

class PowerProfile(Enum):
    """Perfiles de energía disponibles"""
    HIGH_PERFORMANCE = "high_performance"
    BALANCED = "balanced"
    POWER_SAVER = "power_saver"
    ULTRA_LOW = "ultra_low"

@dataclass
class PowerSettings:
    """Configuración de energía para un perfil"""
    name: str
    cpu_min_freq: int  # MHz
    cpu_max_freq: int  # MHz
    cpu_governor: str  # performance, ondemand, conservative, powersave
    screen_brightness: int  # 0-100
    disk_spindown: int  # segundos
    usb_autosuspend: bool
    wifi_power_save: bool
    bluetooth_enabled: bool
    processes_to_suspend: List[str]
    priority_processes: List[str]

@dataclass
class BatteryInfo:
    """Información de batería"""
    percent: float
    time_left: Optional[timedelta]
    power_plugged: bool
    charging: bool

class PowerManager:
    """Gestor inteligente de energía"""

    def __init__(self):
        self.logger = container.get_logger()
        self.config = container.get_config_manager()

        # Perfiles de energía predefinidos
        self.profiles = self._create_default_profiles()
        self.current_profile = PowerProfile.BALANCED
        self.auto_switch_enabled = True

        # Estado del sistema
        self.battery_info = self._get_battery_info()
        self.system_load = self._get_system_load()

        # Historial de transiciones
        self.transition_history: List[Dict] = []

    def _create_default_profiles(self) -> Dict[PowerProfile, PowerSettings]:
        """Crea los perfiles de energía por defecto"""
        return {
            PowerProfile.HIGH_PERFORMANCE: PowerSettings(
                name="Alto Rendimiento",
                cpu_min_freq=800,
                cpu_max_freq=4000,
                cpu_governor="performance",
                screen_brightness=100,
                disk_spindown=300,
                usb_autosuspend=False,
                wifi_power_save=False,
                bluetooth_enabled=True,
                processes_to_suspend=[],
                priority_processes=["game.exe", "render.exe", "compile.exe"]
            ),
            PowerProfile.BALANCED: PowerSettings(
                name="Equilibrado",
                cpu_min_freq=800,
                cpu_max_freq=3000,
                cpu_governor="ondemand",
                screen_brightness=80,
                disk_spindown=180,
                usb_autosuspend=True,
                wifi_power_save=True,
                bluetooth_enabled=True,
                processes_to_suspend=["update.exe", "backup.exe"],
                priority_processes=[]
            ),
            PowerProfile.POWER_SAVER: PowerSettings(
                name="Ahorro de Energía",
                cpu_min_freq=400,
                cpu_max_freq=2000,
                cpu_governor="powersave",
                screen_brightness=50,
                disk_spindown=60,
                usb_autosuspend=True,
                wifi_power_save=True,
                bluetooth_enabled=False,
                processes_to_suspend=["chrome.exe", "spotify.exe", "steam.exe"],
                priority_processes=[]
            ),
            PowerProfile.ULTRA_LOW: PowerSettings(
                name="Ultra Bajo Consumo",
                cpu_min_freq=400,
                cpu_max_freq=1200,
                cpu_governor="powersave",
                screen_brightness=30,
                disk_spindown=30,
                usb_autosuspend=True,
                wifi_power_save=True,
                bluetooth_enabled=False,
                processes_to_suspend=["*"],  # Suspender todos los procesos no críticos
                priority_processes=["backendbot.exe"]
            )
        }

    def _get_battery_info(self) -> BatteryInfo:
        """Obtiene información de la batería"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return BatteryInfo(
                    percent=battery.percent,
                    time_left=timedelta(seconds=battery.secsleft) if battery.secsleft != -1 else None,
                    power_plugged=battery.power_plugged,
                    charging=getattr(battery, 'charging', False)
                )
        except Exception as e:
            self.logger.error(f"Error obteniendo info de batería: {e}")

        return BatteryInfo(
            percent=100.0,
            time_left=None,
            power_plugged=True,
            charging=False
        )

    def _get_system_load(self) -> Dict[str, float]:
        """Obtiene la carga actual del sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

    def apply_profile(self, profile: PowerProfile):
        """Aplica un perfil de energía"""
        if profile not in self.profiles:
            self.logger.error(f"Perfil '{profile.value}' no encontrado")
            return False

        settings = self.profiles[profile]
        self.logger.info(f"Aplicando perfil de energía: {settings.name}")

        try:
            # Aplicar configuración de CPU
            self._set_cpu_settings(settings)

            # Aplicar configuración de pantalla
            self._set_screen_brightness(settings.screen_brightness)

            # Aplicar configuración de disco
            self._set_disk_settings(settings.disk_spindown)

            # Gestionar procesos
            self._manage_processes(settings)

            # Aplicar configuraciones de red
            self._set_network_settings(settings)

            # Registrar transición
            self._log_transition(profile)

            self.current_profile = profile
            self.logger.info(f"Perfil '{settings.name}' aplicado exitosamente")

            return True

        except Exception as e:
            self.logger.error(f"Error aplicando perfil '{settings.name}': {e}")
            return False

    def _set_cpu_settings(self, settings: PowerSettings):
        """Configura los ajustes de CPU"""
        try:
            if platform.system() == "Windows":
                # En Windows, usar powercfg
                if settings.cpu_governor == "performance":
                    subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=True)
                elif settings.cpu_governor == "powersave":
                    subprocess.run(["powercfg", "/setactive", "a1841308-3541-4fab-bc81-f71556f20b4a"], check=True)
            else:
                # En Linux, configurar governor
                governor_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
                if os.path.exists(governor_path):
                    with open(governor_path, 'w') as f:
                        f.write(settings.cpu_governor)
        except Exception as e:
            self.logger.warning(f"No se pudo configurar CPU governor: {e}")

    def _set_screen_brightness(self, brightness: int):
        """Configura el brillo de pantalla"""
        try:
            if platform.system() == "Windows":
                # En Windows, usar WMI o herramientas externas
                pass  # Implementar con WMI o external tools
            else:
                # En Linux, escribir en sysfs
                brightness_path = "/sys/class/backlight/*/brightness"
                for path in glob.glob(brightness_path):
                    max_brightness_path = path.replace("brightness", "max_brightness")
                    if os.path.exists(max_brightness_path):
                        with open(max_brightness_path, 'r') as f:
                            max_brightness = int(f.read().strip())
                        target_brightness = int((brightness / 100) * max_brightness)
                        with open(path, 'w') as f:
                            f.write(str(target_brightness))
        except Exception as e:
            self.logger.warning(f"No se pudo configurar brillo de pantalla: {e}")

    def _set_disk_settings(self, spindown_seconds: int):
        """Configura los ajustes de disco"""
        try:
            if platform.system() == "Linux":
                # Configurar spindown en Linux
                spindown_value = spindown_seconds // 5  # Valor en unidades de 5 segundos
                subprocess.run(["hdparm", "-S", str(spindown_value), "/dev/sda"], check=True)
        except Exception as e:
            self.logger.warning(f"No se pudo configurar spindown de disco: {e}")

    def _manage_processes(self, settings: PowerSettings):
        """Gestiona procesos según el perfil"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()

                    # Suspender procesos no críticos
                    if settings.processes_to_suspend:
                        if ("*" in settings.processes_to_suspend or
                            any(pattern.lower() in proc_name for pattern in settings.processes_to_suspend)):
                            if proc_name not in [p.lower() for p in settings.priority_processes]:
                                proc.suspend()

                    # Reanudar procesos prioritarios
                    if any(pattern.lower() in proc_name for pattern in settings.priority_processes):
                        proc.resume()

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Error gestionando procesos: {e}")

    def _set_network_settings(self, settings: PowerSettings):
        """Configura ajustes de red"""
        try:
            if platform.system() == "Linux":
                # Configurar WiFi power save
                wifi_save = "on" if settings.wifi_power_save else "off"
                subprocess.run(["iwconfig", "wlan0", "power", wifi_save], check=True)

                # Gestionar Bluetooth
                if not settings.bluetooth_enabled:
                    subprocess.run(["systemctl", "stop", "bluetooth"], check=True)
                else:
                    subprocess.run(["systemctl", "start", "bluetooth"], check=True)
        except Exception as e:
            self.logger.warning(f"No se pudo configurar ajustes de red: {e}")

    def _log_transition(self, profile: PowerProfile):
        """Registra una transición de perfil"""
        transition = {
            'timestamp': datetime.now().isoformat(),
            'from_profile': self.current_profile.value if self.current_profile else None,
            'to_profile': profile.value,
            'battery_percent': self.battery_info.percent,
            'power_plugged': self.battery_info.power_plugged,
            'system_load': self.system_load
        }
        self.transition_history.append(transition)

        # Mantener solo las últimas 100 transiciones
        if len(self.transition_history) > 100:
            self.transition_history = self.transition_history[-100:]

    def auto_switch_profile(self):
        """Cambia automáticamente el perfil basado en condiciones"""
        if not self.auto_switch_enabled:
            return

        # Actualizar información del sistema
        self.battery_info = self._get_battery_info()
        self.system_load = self._get_system_load()

        new_profile = self._determine_optimal_profile()

        if new_profile != self.current_profile:
            self.logger.info(f"Cambio automático de perfil: {self.current_profile.value} -> {new_profile.value}")
            self.apply_profile(new_profile)

    def _determine_optimal_profile(self) -> PowerProfile:
        """Determina el perfil óptimo basado en condiciones actuales"""
        battery_percent = self.battery_info.percent
        power_plugged = self.battery_info.power_plugged
        cpu_usage = self.system_load['cpu_percent']

        # Lógica de decisión automática
        if power_plugged:
            if cpu_usage > 70:
                return PowerProfile.HIGH_PERFORMANCE
            else:
                return PowerProfile.BALANCED
        else:  # En batería
            if battery_percent < 20:
                return PowerProfile.ULTRA_LOW
            elif battery_percent < 50:
                return PowerProfile.POWER_SAVER
            else:
                return PowerProfile.BALANCED

    def get_power_status(self) -> Dict:
        """Obtiene el estado actual de energía"""
        return {
            'current_profile': self.current_profile.value,
            'battery_info': {
                'percent': self.battery_info.percent,
                'time_left': str(self.battery_info.time_left) if self.battery_info.time_left else None,
                'power_plugged': self.battery_info.power_plugged,
                'charging': self.battery_info.charging
            },
            'system_load': self.system_load,
            'auto_switch_enabled': self.auto_switch_enabled
        }

    def set_auto_switch(self, enabled: bool):
        """Habilita/deshabilita el cambio automático de perfiles"""
        self.auto_switch_enabled = enabled
        self.config.set('power.auto_switch', enabled)

    def get_transition_history(self, limit: int = 20) -> List[Dict]:
        """Obtiene historial de transiciones de perfil"""
        return self.transition_history[-limit:]

# Instancia global
power_manager = PowerManager()

if __name__ == "__main__":
    # Demo del sistema de gestión de energía
    print("⚡ Demo del Sistema de Gestión de Energía Inteligente")

    # Mostrar estado actual
    status = power_manager.get_power_status()
    print(f"📊 Estado actual: {json.dumps(status, indent=2, default=str)}")

    # Aplicar perfil de alto rendimiento
    print("\n🏃 Aplicando perfil de Alto Rendimiento...")
    power_manager.apply_profile(PowerProfile.HIGH_PERFORMANCE)

    # Simular cambio automático
    print("\n🔄 Simulando cambio automático...")
    power_manager.auto_switch_profile()

    # Mostrar historial
    history = power_manager.get_transition_history()
    print(f"\n📋 Historial de transiciones: {len(history)}")

    print("\n✅ Sistema de gestión de energía inicializado correctamente!")