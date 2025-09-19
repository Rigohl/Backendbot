import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Integration tests for Bot Monitor
# Note: These require Redis running

def test_monitor_import():
    """Test that the monitor module can be imported."""
    try:
        from backendbot.bots.bot_monitor import monitor_worker, STATS_LATEST_KEY
        assert STATS_LATEST_KEY == "system_stats_latest"
    except ImportError:
        assert False, "Failed to import monitor"

# TODO: Implement full integration tests when Redis is running
# def test_monitor_publishes_stats():
#     # This would require starting Redis, running the monitor briefly, and checking the key
#     pass