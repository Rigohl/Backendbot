# BackendBot package initialization with optional dependencies
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional dependencies - check availability without importing
try:
    import GPUtil  # noqa: F401
    GPU_AVAILABLE = True
    logger.info("GPUtil available for GPU monitoring")
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("GPUtil not available - GPU monitoring disabled")

try:
    import wmi  # noqa: F401
    WMI_AVAILABLE = True
    logger.info("WMI available for Windows management")
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("WMI not available - Windows management features limited")

try:
    import psutil  # noqa: F401
    PSUTIL_AVAILABLE = True
    logger.info("psutil available for system monitoring")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.error("psutil not available - system monitoring disabled")

# Export availability flags
__all__ = ["GPU_AVAILABLE", "WMI_AVAILABLE", "PSUTIL_AVAILABLE"]