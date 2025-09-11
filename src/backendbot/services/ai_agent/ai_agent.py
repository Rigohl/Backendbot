# AI Agent Service - Integración de IA para análisis inteligente
# Buenas prácticas: Modular, con configuración segura, manejo de errores

import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from .ai_service import AIService  # Importar servicio base existente

logger = logging.getLogger(__name__)

class AIAgent:
    """
    Agente de IA para análisis inteligente de métricas y optimizaciones automáticas.
    Usa OpenAI para análisis predictivo y recomendaciones.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.ai_service = AIService()
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
    async def analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza métricas del sistema usando IA para detectar anomalías y recomendaciones.
        
        Args:
            metrics: Diccionario con métricas del sistema
            
        Returns:
            Análisis con recomendaciones y predicciones
        """
        try:
            # Crear prompt para análisis
            prompt = self._create_analysis_prompt(metrics)
            
            # Llamar a OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Enriquecer con datos del servicio base
            enriched_analysis = await self.ai_service.enrich_analysis(analysis, metrics)
            
            logger.info("Análisis de IA completado exitosamente")
            return enriched_analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de IA: {e}")
            return {
                "error": str(e),
                "recommendations": ["Revisar configuración de OpenAI API"],
                "anomalies": []
            }
    
    async def predict_optimization(self, historical_data: list) -> Dict[str, Any]:
        """
        Predice optimizaciones basadas en datos históricos usando IA.
        
        Args:
            historical_data: Lista de datos históricos
            
        Returns:
            Predicciones y recomendaciones de optimización
        """
        try:
            prompt = self._create_prediction_prompt(historical_data)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2
            )
            
            prediction = json.loads(response.choices[0].message.content)
            
            logger.info("Predicción de optimización completada")
            return prediction
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {"error": str(e), "predictions": []}
    
    def _create_analysis_prompt(self, metrics: Dict[str, Any]) -> str:
        """Crea prompt para análisis de métricas."""
        return f"""
        Analiza las siguientes métricas del sistema y proporciona recomendaciones inteligentes:
        
        Métricas actuales:
        {json.dumps(metrics, indent=2)}
        
        Por favor, responde en formato JSON con:
        {{
            "anomalies": ["lista de anomalías detectadas"],
            "recommendations": ["lista de recomendaciones específicas"],
            "risk_level": "bajo|medio|alto",
            "predicted_trends": ["tendencias esperadas"],
            "optimization_suggestions": ["sugerencias de optimización"]
        }}
        
        Sé específico y práctico en tus recomendaciones.
        """
    
    def _create_prediction_prompt(self, historical_data: list) -> str:
        """Crea prompt para predicciones."""
        return f"""
        Basado en los siguientes datos históricos, predice optimizaciones futuras:
        
        Datos históricos:
        {json.dumps(historical_data[-10:], indent=2)}  # Últimos 10 registros
        
        Responde en formato JSON con:
        {{
            "predicted_ram_usage": "predicción en MB",
            "predicted_cpu_usage": "predicción en %",
            "optimization_schedule": ["horarios recomendados para optimización"],
            "resource_alerts": ["alertas preventivas"]
        }}
        """
    
    async def generate_report(self, analysis: Dict[str, Any]) -> str:
        """
        Genera un reporte ejecutivo basado en el análisis de IA.
        
        Args:
            analysis: Resultado del análisis
            
        Returns:
            Reporte en formato markdown
        """
        try:
            prompt = f"""
            Genera un reporte ejecutivo basado en este análisis:
            {json.dumps(analysis, indent=2)}
            
            El reporte debe incluir:
            - Resumen ejecutivo
            - Anomalías críticas
            - Recomendaciones prioritarias
            - Próximos pasos
            
            Formato: Markdown con encabezados claros.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return f"# Error en Reporte\n\nNo se pudo generar el reporte: {e}"

# Instancia global del agente
ai_agent = AIAgent()