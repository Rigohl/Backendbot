"""
Sistema de Aprendizaje Adaptativo para BackendBot
Aprende patrones de uso y optimiza automáticamente el comportamiento.
"""
import json
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
from pathlib import Path
from ..utils.data_store import read_json, write_json, initialize_defaults
import statistics
from ..modes import mode_manager
from ..utils.logging_config import logger

class AdaptiveLearningSystem:
    def __init__(self, data_dir: str = ".backendbot_data"):
        # Ensure data directory and defaults exist
        initialize_defaults()

        # Archivos de datos (nombre sólo)
        self.usage_patterns_file = "usage_patterns.json"
        self.user_preferences_file = "user_preferences.json"
        self.performance_metrics_file = "performance_metrics.json"

        # Datos en memoria
        self.usage_patterns = read_json(self.usage_patterns_file) or defaultdict(lambda: defaultdict(int))
        # normalize to dict
        if isinstance(self.usage_patterns, dict):
            pass
        else:
            self.usage_patterns = dict(self.usage_patterns)

        self.user_preferences = read_json(self.user_preferences_file) or {}
        self.performance_metrics = read_json(self.performance_metrics_file) or defaultdict(list)

        # Estado del aprendizaje
        self.learning_active = True
        self.last_save = time.time()
        self.save_interval = 300  # 5 minutos

        # Iniciar hilo de aprendizaje automático
        self.learning_thread = threading.Thread(target=self._continuous_learning, daemon=True)
        self.learning_thread.start()

        logger.info("Sistema de aprendizaje adaptativo inicializado")

    def _load_data(self, file_path: Path, default_value: Any) -> Any:
        """Cargar datos desde archivo con valor por defecto"""
        # Deprecated: kept for compatibility but now using data_store
        try:
            return default_value
        except Exception:
            return default_value

    def _save_data(self, file_path: Path, data: Any):
        """Guardar datos en archivo"""
        # Use data_store write_json when possible
        try:
            # file_path may be a Path or a string filename
            name = file_path if isinstance(file_path, str) else Path(file_path).name
            write_json(name, data)
        except Exception as e:
            logger.error(f"Error guardando {file_path}: {e}")

    def _continuous_learning(self):
        """Aprendizaje continuo en segundo plano"""
        while self.learning_active:
            try:
                current_time = time.time()

                # Guardar datos periódicamente
                if current_time - self.last_save > self.save_interval:
                    self._save_all_data()
                    self.last_save = current_time

                # Analizar patrones y generar insights
                self._analyze_patterns()
                self._optimize_settings()

                time.sleep(60)  # Analizar cada minuto

            except Exception as e:
                logger.error(f"Error en aprendizaje continuo: {e}")
                time.sleep(300)  # Esperar 5 minutos en caso de error

    def _save_all_data(self):
        """Guardar todos los datos"""
        self._save_data(self.usage_patterns_file, dict(self.usage_patterns))
        self._save_data(self.user_preferences_file, self.user_preferences)
        self._save_data(self.performance_metrics_file, dict(self.performance_metrics))

    def record_user_action(self, action_type: str, action_data: Dict[str, Any]):
        """Registrar una acción del usuario para aprendizaje"""
        try:
            timestamp = datetime.now()
            hour = timestamp.hour
            day_of_week = timestamp.weekday()

            # Registrar por tipo de acción
            if action_type not in self.usage_patterns:
                self.usage_patterns[action_type] = defaultdict(int)

            # Patrones por hora del día
            self.usage_patterns[action_type][f"hour_{hour}"] += 1

            # Patrones por día de la semana
            self.usage_patterns[action_type][f"day_{day_of_week}"] += 1

            # Patrones específicos de la acción
            for key, value in action_data.items():
                pattern_key = f"{key}_{value}"
                self.usage_patterns[action_type][pattern_key] += 1

            # Registrar timestamp para análisis temporal
            if 'timestamps' not in self.usage_patterns[action_type]:
                self.usage_patterns[action_type]['timestamps'] = []
            self.usage_patterns[action_type]['timestamps'].append(timestamp.isoformat())

            # Limitar historial de timestamps (últimos 1000)
            timestamps = self.usage_patterns[action_type]['timestamps']
            if len(timestamps) > 1000:
                self.usage_patterns[action_type]['timestamps'] = timestamps[-1000:]

        except Exception as e:
            logger.error(f"Error registrando acción {action_type}: {e}")

    def learn_pattern(self, pattern_name: str, pattern: Dict[str, Any]):
        """Registrar un patrón aprendido explícitamente (API de compatibilidad para tests)."""
        try:
            # Guardar en memoria bajo patrones aprendidos
            if 'learned_patterns' not in self.usage_patterns:
                self.usage_patterns['learned_patterns'] = {}

            if 'learned_counters' not in self.usage_patterns:
                self.usage_patterns['learned_counters'] = {}

            # Incremental key per ocurrencia: pattern_name_1, pattern_name_2, ...
            counter = self.usage_patterns['learned_counters'].get(pattern_name, 0) + 1
            self.usage_patterns['learned_counters'][pattern_name] = counter

            occurrence_key = f"{pattern_name}_{counter}"
            # Store occurrence
            self.usage_patterns['learned_patterns'][occurrence_key] = pattern

            # Keep base key mapping to most recent occurrence for backward compatibility
            self.usage_patterns['learned_patterns'][pattern_name] = pattern
            # Persistir inmediatamente
            self._save_all_data()
            logger.info(f"Patrón aprendido: {pattern_name}")
        except Exception as e:
            logger.error(f"Error aprendiendo patrón {pattern_name}: {e}")

    @property
    def patterns(self) -> Dict[str, Any]:
        """Exponer patrones aprendidos como diccionario (compatibilidad con tests)."""
        # Construir un diccionario que incluya tanto las ocurrencias
        # individuales (pattern_name_1, pattern_name_2, ...) como la
        # clave base (pattern_name) apuntando a la última ocurrencia.
        learned = self.usage_patterns.get('learned_patterns', {})
        result: Dict[str, Any] = {}

        for k, v in learned.items():
            # Si el valor es una lista de ocurrencias, exponer cada una
            if isinstance(v, list):
                for idx, item in enumerate(v, start=1):
                    occ_key = f"{k}_{idx}"
                    result[occ_key] = item
                # base -> última
                if v:
                    result[k] = v[-1]
                else:
                    result[k] = {}
            else:
                # Si la clave ya tiene sufijo numérico la incluimos tal cual
                result[k] = v

        return result

    @property
    def patterns_list(self) -> Dict[str, List[Any]]:
        """Exponer todas las ocurrencias por patrón como listas.

        Útil cuando se necesita analizar frecuencia o histórico completo.
        """
        learned = self.usage_patterns.get('learned_patterns', {})
        occurrences: Dict[str, List[Any]] = {}
        for k, v in learned.items():
            if isinstance(k, str) and k.rsplit('_', 1)[-1].isdigit():
                base = '_'.join(k.split('_')[:-1])
                occurrences.setdefault(base, []).append(v)
            else:
                occurrences.setdefault(k, []).append(v)

        return occurrences

    def record_performance_metric(self, metric_name: str, value: float, context: Dict[str, Any] = None):
        """Registrar métricas de rendimiento"""
        try:
            metric_data = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }

            if metric_name not in self.performance_metrics:
                self.performance_metrics[metric_name] = []

            self.performance_metrics[metric_name].append(metric_data)

            # Mantener solo las últimas 500 métricas por tipo
            if len(self.performance_metrics[metric_name]) > 500:
                self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-500:]

        except Exception as e:
            logger.error(f"Error registrando métrica {metric_name}: {e}")

    def get_usage_patterns(self, action_type: str = None) -> Dict[str, Any]:
        """Obtener patrones de uso aprendidos"""
        if action_type:
            return dict(self.usage_patterns.get(action_type, {}))
        return dict(self.usage_patterns)

    def predict_user_behavior(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predecir comportamiento del usuario basado en contexto"""
        try:
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()

            predictions = {}

            for action_type, patterns in self.usage_patterns.items():
                # Calcular probabilidad basada en hora actual
                hour_key = f"hour_{current_hour}"
                hour_count = patterns.get(hour_key, 0)
                total_actions = sum(count for key, count in patterns.items()
                                  if key.startswith('hour_') or key.startswith('day_'))

                if total_actions > 0:
                    hour_probability = hour_count / total_actions
                    predictions[action_type] = {
                        'probability': hour_probability,
                        'confidence': min(hour_count / 10, 1.0),  # Confianza basada en frecuencia
                        'context_match': self._calculate_context_match(context, patterns)
                    }

            # Ordenar por probabilidad
            sorted_predictions = sorted(predictions.items(),
                                      key=lambda x: x[1]['probability'],
                                      reverse=True)

            return dict(sorted_predictions[:5])  # Top 5 predicciones

        except Exception as e:
            logger.error(f"Error en predicción de comportamiento: {e}")
            return {}

    def _calculate_context_match(self, context: Dict[str, Any], patterns: Dict[str, Any]) -> float:
        """Calcular qué tan bien coincide el contexto con los patrones aprendidos"""
        try:
            matches = 0
            total_patterns = 0

            for key, value in context.items():
                pattern_key = f"{key}_{value}"
                if pattern_key in patterns:
                    matches += patterns[pattern_key]
                total_patterns += 1

            return matches / max(total_patterns, 1)

        except Exception:
            return 0.0

    def _analyze_patterns(self):
        """Analizar patrones y generar insights"""
        try:
            insights = {}

            for action_type, patterns in self.usage_patterns.items():
                # Analizar patrones temporales
                hour_patterns = {k: v for k, v in patterns.items() if k.startswith('hour_')}
                if hour_patterns:
                    peak_hour = max(hour_patterns.items(), key=lambda x: x[1])
                    insights[f"{action_type}_peak_hour"] = peak_hour[0].replace('hour_', '')

                # Analizar patrones por día
                day_patterns = {k: v for k, v in patterns.items() if k.startswith('day_')}
                if day_patterns:
                    preferred_day = max(day_patterns.items(), key=lambda x: x[1])
                    insights[f"{action_type}_preferred_day"] = preferred_day[0].replace('day_', '')

            # Actualizar preferencias del usuario
            self.user_preferences.update(insights)

        except Exception as e:
            logger.error(f"Error analizando patrones: {e}")

    def _optimize_settings(self):
        """Optimizar configuraciones basado en aprendizaje"""
        try:
            # Optimizar intervalos de monitoreo basado en patrones de uso
            usage_intensity = self._calculate_usage_intensity()

            if usage_intensity > 0.7:  # Uso intensivo
                optimal_interval = 2
            elif usage_intensity > 0.4:  # Uso moderado
                optimal_interval = 5
            else:  # Uso ligero
                optimal_interval = 10

            # Aplicar optimización si es significativamente diferente
            current_interval = mode_manager.get_monitoring_interval()
            if abs(current_interval - optimal_interval) >= 2:
                logger.info(f"Optimizando intervalo de monitoreo: {current_interval} -> {optimal_interval}")
                # Nota: En una implementación real, ajustaríamos el intervalo del mode_manager

        except Exception as e:
            logger.error(f"Error optimizando configuraciones: {e}")

    def _calculate_usage_intensity(self) -> float:
        """Calcular intensidad de uso del sistema"""
        try:
            # Basado en acciones recientes (última hora)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_actions = 0
            total_actions = 0

            for action_type, patterns in self.usage_patterns.items():
                timestamps = patterns.get('timestamps', [])
                for ts_str in timestamps:
                    try:
                        ts = datetime.fromisoformat(ts_str)
                        total_actions += 1
                        if ts > one_hour_ago:
                            recent_actions += 1
                    except:
                        pass

            return recent_actions / max(total_actions, 1)

        except Exception:
            return 0.5  # Valor por defecto moderado

    def get_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en aprendizaje"""
        recommendations = []

        try:
            # Recomendaciones basadas en patrones de uso
            usage_patterns = self.get_usage_patterns()

            if usage_patterns:
                # Recomendar modo basado en patrones
                current_mode = mode_manager.get_mode_info()['mode']
                recommended_mode = self._recommend_optimal_mode()

                if recommended_mode and recommended_mode != current_mode:
                    recommendations.append(f"Considera cambiar al modo '{recommended_mode}' basado en tus patrones de uso")

                # Recomendaciones de optimización
                if self._should_enable_aggressive_cleanup():
                    recommendations.append("Se recomienda activar limpieza agresiva basada en patrones de archivos")

                # Recomendaciones de rendimiento
                performance_insights = self._analyze_performance_trends()
                recommendations.extend(performance_insights)

        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")

        return recommendations

    def get_recommendation(self, action_type: str) -> Optional[Dict[str, Any]]:
        """Retornar una recomendación simple para un tipo de acción dado."""
        try:
            patterns = self.usage_patterns.get('learned_patterns', {})
            # Buscar la primera entrada que coincida con action_type
            for pname, entries in patterns.items():
                if isinstance(entries, list):
                    for e in entries:
                        if e.get('action') == action_type:
                            return e
                elif isinstance(entries, dict):
                    if entries.get('action') == action_type:
                        return entries
            return None
        except Exception:
            return None

    def _recommend_optimal_mode(self) -> Optional[str]:
        """Recomendar el modo óptimo basado en patrones"""
        try:
            # Análisis simplificado basado en tipos de acciones
            action_types = list(self.usage_patterns.keys())

            if any('code' in action or 'editor' in action for action in action_types):
                return 'editor'
            elif any('stream' in action or 'record' in action for action in action_types):
                return 'streaming'
            elif any('game' in action for action in action_types):
                return 'gaming'
            elif len(action_types) > 10:  # Muchos tipos diferentes
                return 'desarrollo'
            else:
                return 'relax'

        except Exception:
            return None

    def _should_enable_aggressive_cleanup(self) -> bool:
        """Determinar si se debe activar limpieza agresiva"""
        try:
            # Basado en cantidad de archivos temporales/cache encontrados
            temp_patterns = [k for k in self.usage_patterns.keys() if 'temp' in k or 'cache' in k]
            return len(temp_patterns) > 5
        except Exception:
            return False

    def _analyze_performance_trends(self) -> List[str]:
        """Analizar tendencias de rendimiento"""
        insights = []

        try:
            for metric_name, metrics in self.performance_metrics.items():
                if len(metrics) < 10:  # Necesitamos suficientes datos
                    continue

                values = [m['value'] for m in metrics[-20:]]  # Últimas 20 métricas

                if len(values) >= 10:
                    mean = statistics.mean(values)
                    std_dev = statistics.stdev(values) if len(values) > 1 else 0

                    # Detectar tendencias
                    if metric_name == 'cpu_usage' and mean > 80:
                        insights.append("Uso alto de CPU detectado, considera optimizaciones")
                    elif metric_name == 'memory_usage' and mean > 85:
                        insights.append("Uso alto de memoria, posible necesidad de limpieza")

        except Exception as e:
            logger.error(f"Error analizando rendimiento: {e}")

        return insights

    def get_learning_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de aprendizaje"""
        return {
            'total_actions_learned': len(self.usage_patterns),
            'total_metrics_recorded': sum(len(metrics) for metrics in self.performance_metrics.values()),
            'patterns_analyzed': len(self.user_preferences),
            'learning_active': self.learning_active,
            'data_files': [
                str(self.usage_patterns_file),
                str(self.user_preferences_file),
                str(self.performance_metrics_file)
            ]
        }

    def stop_learning(self):
        """Detener el aprendizaje automático"""
        self.learning_active = False
        self._save_all_data()
        logger.info("Sistema de aprendizaje adaptativo detenido")

# Instancia global del sistema de aprendizaje
adaptive_learning = AdaptiveLearningSystem()

# Alias de compatibilidad: algunos tests esperan una clase `AdaptiveLearning`
class AdaptiveLearning(AdaptiveLearningSystem):
    pass
