#!/usr/bin/env python3
"""
Sistema de Notificaciones Avanzado - BackendBot
Implementa notificaciones por email, escritorio, sonidos y gestión inteligente
"""
import os
import sys
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, time
import winsound  # Para sonidos en Windows
import plyer  # Para notificaciones de escritorio

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.core.di.container import container

@dataclass
class NotificationRule:
    """Regla para determinar cuándo enviar notificaciones"""
    name: str
    condition: str  # Ej: "cpu > 80", "memory > 85"
    priority: str   # "low", "medium", "high", "critical"
    channels: List[str]  # ["desktop", "email", "sound"]
    cooldown_minutes: int = 5
    enabled: bool = True

@dataclass
class NotificationHistory:
    """Historial de notificaciones enviadas"""
    timestamp: datetime
    rule_name: str
    message: str
    channels: List[str]
    priority: str

class NotificationManager:
    """Gestor centralizado de notificaciones"""

    def __init__(self):
        self.logger = container.get_logger()
        self.config = container.get_config_manager()

        # Configuración de email
        self.smtp_server = self.config.get('notifications.smtp.server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('notifications.smtp.port', 587)
        self.email_user = self.config.get('notifications.email.user')
        self.email_password = self.config.get('notifications.email.password')
        self.email_recipients = self.config.get('notifications.email.recipients', [])

        # Configuración de sonidos
        self.sound_enabled = self.config.get('notifications.sound.enabled', True)
        self.sound_files = {
            'low': 'sounds/notification_low.wav',
            'medium': 'sounds/notification_medium.wav',
            'high': 'sounds/notification_high.wav',
            'critical': 'sounds/notification_critical.wav'
        }

        # Reglas de notificación
        self.rules: Dict[str, NotificationRule] = {}
        self.history: List[NotificationHistory] = []
        self.last_notifications: Dict[str, datetime] = {}

        self._load_rules()
        self._create_sound_files()

    def _load_rules(self):
        """Carga las reglas de notificación desde configuración"""
        default_rules = [
            NotificationRule(
                name="cpu_high",
                condition="cpu > 80",
                priority="high",
                channels=["desktop", "sound"],
                cooldown_minutes=10
            ),
            NotificationRule(
                name="memory_critical",
                condition="memory > 90",
                priority="critical",
                channels=["desktop", "email", "sound"],
                cooldown_minutes=5
            ),
            NotificationRule(
                name="disk_space_low",
                condition="disk_free < 10",
                priority="high",
                channels=["desktop", "email"],
                cooldown_minutes=60
            ),
            NotificationRule(
                name="backup_completed",
                condition="backup_status == 'completed'",
                priority="low",
                channels=["desktop"],
                cooldown_minutes=0
            )
        ]

        # Cargar reglas desde configuración o usar defaults
        configured_rules = self.config.get('notifications.rules', [])
        if configured_rules:
            for rule_data in configured_rules:
                rule = NotificationRule(**rule_data)
                self.rules[rule.name] = rule
        else:
            for rule in default_rules:
                self.rules[rule.name] = rule

    def _create_sound_files(self):
        """Crea archivos de sonido básicos si no existen"""
        sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
        os.makedirs(sounds_dir, exist_ok=True)

        # Crear sonidos básicos usando winsound
        # Nota: En producción, usar archivos WAV reales
        pass

    def _check_cooldown(self, rule_name: str) -> bool:
        """Verifica si ha pasado el tiempo de cooldown para una regla"""
        if rule_name not in self.last_notifications:
            return True

        last_time = self.last_notifications[rule_name]
        cooldown_minutes = self.rules[rule_name].cooldown_minutes
        return (datetime.now() - last_time).total_seconds() > (cooldown_minutes * 60)

    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Evalúa una condición usando el contexto proporcionado"""
        try:
            # Reemplazar variables en la condición
            for key, value in context.items():
                if isinstance(value, (int, float)):
                    condition = condition.replace(key, str(value))
                elif isinstance(value, str):
                    condition = condition.replace(key, f"'{value}'")

            # Evaluar la condición de forma segura
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            self.logger.error(f"Error evaluando condición '{condition}': {e}")
            return False

    def _send_desktop_notification(self, title: str, message: str, priority: str):
        """Envía notificación de escritorio"""
        try:
            icon_path = self._get_priority_icon(priority)
            plyer.notification.notify(
                title=title,
                message=message,
                app_name="BackendBot",
                app_icon=icon_path
            )
        except Exception as e:
            self.logger.error(f"Error enviando notificación desktop: {e}")

    def _send_email_notification(self, subject: str, message: str):
        """Envía notificación por email"""
        if not all([self.email_user, self.email_password, self.email_recipients]):
            self.logger.warning("Configuración de email incompleta")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.email_recipients)
            msg['Subject'] = f"BackendBot - {subject}"

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, self.email_recipients, text)
            server.quit()

            self.logger.info(f"Email enviado a {len(self.email_recipients)} destinatarios")
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")

    def _play_sound_notification(self, priority: str):
        """Reproduce sonido de notificación"""
        if not self.sound_enabled:
            return

        try:
            sound_file = self.sound_files.get(priority, self.sound_files['medium'])
            if os.path.exists(sound_file):
                winsound.PlaySound(sound_file, winsound.SND_FILENAME)
            else:
                # Sonido por defecto del sistema
                winsound.MessageBeep(winsound.SND_ALIAS)
        except Exception as e:
            self.logger.error(f"Error reproduciendo sonido: {e}")

    def _get_priority_icon(self, priority: str) -> str:
        """Obtiene el ícono según la prioridad"""
        icons_dir = os.path.join(os.path.dirname(__file__), 'ui', 'icons')
        icon_map = {
            'low': 'info.ico',
            'medium': 'warning.ico',
            'high': 'alert.ico',
            'critical': 'critical.ico'
        }
        icon_file = icon_map.get(priority, 'info.ico')
        return os.path.join(icons_dir, icon_file)

    def send_notification(self, rule_name: str, context: Dict = None):
        """Envía notificación basada en una regla"""
        if rule_name not in self.rules:
            self.logger.warning(f"Regla '{rule_name}' no encontrada")
            return

        rule = self.rules[rule_name]
        if not rule.enabled:
            return

        # Verificar cooldown
        if not self._check_cooldown(rule_name):
            return

        # Evaluar condición si hay contexto
        if context and not self._evaluate_condition(rule.condition, context):
            return

        # Preparar mensaje
        title = f"BackendBot - {rule.name.replace('_', ' ').title()}"
        message = self._generate_message(rule_name, context or {})

        # Enviar por cada canal configurado
        for channel in rule.channels:
            if channel == "desktop":
                self._send_desktop_notification(title, message, rule.priority)
            elif channel == "email":
                self._send_email_notification(title, message)
            elif channel == "sound":
                self._play_sound_notification(rule.priority)

        # Registrar en historial
        notification = NotificationHistory(
            timestamp=datetime.now(),
            rule_name=rule_name,
            message=message,
            channels=rule.channels.copy(),
            priority=rule.priority
        )
        self.history.append(notification)
        self.last_notifications[rule_name] = datetime.now()

        self.logger.info(f"Notificación '{rule_name}' enviada por canales: {rule.channels}")

    def _generate_message(self, rule_name: str, context: Dict) -> str:
        """Genera mensaje personalizado basado en la regla y contexto"""
        messages = {
            "cpu_high": f"Uso de CPU alto detectado: {context.get('cpu', 'N/A')}%",
            "memory_critical": f"Memoria crítica: {context.get('memory', 'N/A')}% utilizada",
            "disk_space_low": f"Espacio en disco bajo: {context.get('disk_free', 'N/A')}GB libres",
            "backup_completed": "Backup completado exitosamente"
        }
        return messages.get(rule_name, f"Notificación: {rule_name}")

    def get_notification_history(self, limit: int = 50) -> List[NotificationHistory]:
        """Obtiene historial de notificaciones"""
        return self.history[-limit:]

    def update_rule(self, rule_name: str, **updates):
        """Actualiza una regla de notificación"""
        if rule_name in self.rules:
            for key, value in updates.items():
                if hasattr(self.rules[rule_name], key):
                    setattr(self.rules[rule_name], key, value)
            self._save_rules()

    def _save_rules(self):
        """Guarda las reglas en configuración"""
        rules_data = [vars(rule) for rule in self.rules.values()]
        self.config.set('notifications.rules', rules_data)

    def get_silence_mode(self) -> bool:
        """Verifica si está en modo silencio"""
        silence_config = self.config.get('notifications.silence', {})
        enabled = silence_config.get('enabled', False)
        if not enabled:
            return False

        start_time = silence_config.get('start_time')
        end_time = silence_config.get('end_time')

        if start_time and end_time:
            now = datetime.now().time()
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
            return start <= now <= end

        return False

    def set_silence_mode(self, enabled: bool, start_time: str = None, end_time: str = None):
        """Configura modo silencio"""
        silence_config = {
            'enabled': enabled,
            'start_time': start_time,
            'end_time': end_time
        }
        self.config.set('notifications.silence', silence_config)

# Instancia global
notification_manager = NotificationManager()

if __name__ == "__main__":
    # Demo del sistema de notificaciones
    print("🔔 Demo del Sistema de Notificaciones Avanzado")

    # Simular algunas notificaciones
    notification_manager.send_notification("cpu_high", {"cpu": 85})
    notification_manager.send_notification("memory_critical", {"memory": 92})

    # Mostrar historial
    history = notification_manager.get_notification_history()
    print(f"\n📋 Historial de notificaciones: {len(history)}")

    print("\n✅ Sistema de notificaciones inicializado correctamente!")