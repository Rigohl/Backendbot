import os
from pkgutil import extend_path
import sys

# Ensure project `src` directory is on sys.path so imports like
# `src.backendbot...` resolve inside pytest and scripts.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_SRC_DIR = os.path.join(_PROJECT_ROOT, "src")
if os.path.isdir(_SRC_DIR) and _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Namespace package shim: prefer local `src/backendbot` sources for imports.
__path__ = extend_path(__path__, __name__)
_ROOT = os.path.dirname(os.path.dirname(__file__))
_SRC_BACKENDBOT = os.path.normpath(os.path.join(_ROOT, "src", "backendbot"))
if os.path.isdir(_SRC_BACKENDBOT) and _SRC_BACKENDBOT not in __path__:
    __path__.insert(0, _SRC_BACKENDBOT)

__all__ = []
