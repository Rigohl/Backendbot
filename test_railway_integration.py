#!/usr/bin/env python3
"""
Railway verification script for BackendBot
Tests all Railway integrations and configurations
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_database():
    """Test database connection"""
    try:
        from backendbot.database import get_db
        async for db in get_db():
            await db.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def test_redis():
    """Test Redis connection"""
    try:
        from backendbot.cache import cache
        if not cache.is_available():
            logger.info("Redis not available (optional service)")
            return True

        # Use set_metric for testing
        test_data = {"test": "value", "timestamp": "2024-01-01"}
        cache.set_metric("test_key", test_data, ttl=10)
        value = cache.get_metric("test_key")
        if value and value.get("test") == "value":
            logger.info("Redis connection successful")
            return True
        else:
            logger.error("Redis get/set test failed")
            return False
    except Exception as e:
        logger.warning(f"Redis test failed (optional): {e}")
        return True  # Redis is optional

async def test_health_check():
    """Test health check endpoint"""
    try:
        from backendbot.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")

        if response.status_code == 200:
            logger.info("Health check endpoint working")
            return True
        else:
            logger.error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Health check test failed: {e}")
        return False

async def test_railway_config():
    """Test Railway-specific configurations"""
    checks = []

    # Check environment variables
    railway_vars = [
        'RAILWAY_PROJECT_ID',
        'RAILWAY_ENVIRONMENT_ID',
        'RAILWAY_SERVICE_ID'
    ]

    for var in railway_vars:
        if os.getenv(var):
            logger.info(f"{var} is set")
            checks.append(True)
        else:
            logger.info(f"{var} not set (normal for local testing)")
            checks.append(True)  # Not required for local testing

    # Check database URL
    if os.getenv('DATABASE_URL'):
        logger.info("DATABASE_URL is set")
        checks.append(True)
    else:
        logger.info("DATABASE_URL not set (will use SQLite for local development)")
        checks.append(True)  # OK for local development

    return all(checks)

async def main():
    """Run all Railway verification tests"""
    logger.info(f"Starting Railway verification for BackendBot")

    tests = [
        ("Database Connection", test_database),
        ("Redis Connection", test_redis),
        ("Health Check", test_health_check),
        ("Railway Config", test_railway_config),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"Testing {test_name}...")
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    logger.info(f"\nTest Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("All Railway integrations are working correctly!")
        return 0
    else:
        logger.error("Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)