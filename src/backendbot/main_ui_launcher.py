#!/usr/bin/env python3
"""
Punto de entrada principal para BackendBot UI
Lanza la interfaz de usuario completa con icono de bandeja y panel flotante
"""
import sys
import os
from pathlib import Path

# Configurar paths correctamente
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

def main():
    """Función principal que inicia BackendBot"""
    try:
        # Importar después de configurar paths
        from backendbot.main_integrated import main as run_integrated_backendbot

        # Ejecutar BackendBot Integrado
        run_integrated_backendbot()

    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Verifica que todas las dependencias estén instaladas:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"Error iniciando BackendBot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()