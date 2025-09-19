#!/usr/bin/env python3
"""
Launcher principal para BackendBot con configuración correcta de paths
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path de Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Ahora importar los módulos
try:
    from backendbot.core.env import ensure_loaded
    ensure_loaded()
except Exception:
    pass

from src.backendbot.main_ui_launcher import main

if __name__ == "__main__":
    main()