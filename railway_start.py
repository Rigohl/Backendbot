#!/usr/bin/env python3
"""
Railway startup script for BackendBot
Handles environment variables and proper initialization
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path for Railway
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_environment():
    """Setup environment variables for Railway"""
    # Railway provides PORT automatically
    port = os.getenv('PORT', '8000')

    # Set default environment if not set
    if not os.getenv('ENVIRONMENT'):
        os.environ['ENVIRONMENT'] = 'production'

    # Set log level
    if not os.getenv('LOG_LEVEL'):
        os.environ['LOG_LEVEL'] = 'INFO'

    # Database URL should be provided by Railway
    if not os.getenv('DATABASE_URL'):
        logger.warning("DATABASE_URL not set - using SQLite fallback")
        os.environ['DATABASE_URL'] = 'sqlite:///./backendbot.db'

    logger.info(f"Environment: {os.getenv('ENVIRONMENT')}")
    logger.info(f"Database: {'PostgreSQL' if 'postgresql' in os.getenv('DATABASE_URL', '') else 'SQLite'}")

    return port

def main():
    """Main startup function"""
    try:
        port = setup_environment()

        # Import the FastAPI app
        from backendbot.main import app
        logger.info("✅ BackendBot app loaded successfully")

        host = os.environ.get("HOST", "0.0.0.0")

        logger.info(f"🚀 Starting BackendBot on {host}:{port}")

        # Run with Railway's configuration
        uvicorn.run(
            "backendbot.main:app",
            host=host,
            port=int(port),
            reload=False,
            workers=1,
            loop="uvloop",
            http="httptools",
            log_level="info"
        )

    except ImportError as e:
        logger.error(f"❌ Error importing app: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start BackendBot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()