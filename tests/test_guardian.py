import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Tests for Bot Guardian integration
# Note: These are placeholders for integration tests
# Full integration would require running the bots and checking restarts

def test_guardian_import():
    """Test that the guardian module can be imported."""
    try:
        from backendbot.bots.bot_guardian import guardian_worker, BOTS_TO_MANAGE
        assert len(BOTS_TO_MANAGE) == 3  # Monitor, Organizer, Indexer
    except ImportError:
        assert False, "Failed to import guardian"

# TODO: Implement full integration tests when Redis and bots are running
# def test_guardian_restarts_bot():
#     # This would require mocking subprocess or running in a controlled environment
#     pass