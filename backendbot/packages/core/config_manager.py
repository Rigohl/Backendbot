"""
Database Config Manager for BackendBot.
"""
import json
from .config import Settings
from backendbot.core.database.manager import get_db
from backendbot.core.database.models import Setting

class DatabaseConfigManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.load_from_db()

    def load_from_db(self):
        with get_db() as db:
            db_settings = db.query(Setting).all()
            settings_dict = {s.key: json.loads(s.value) for s in db_settings}
            
            # Update pydantic settings with values from DB
            # This is a simplified example. A real implementation would
            # recursively update the nested settings objects.
            for key, value in settings_dict.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)

    def save_to_db(self):
        with get_db() as db:
            settings_dict = self.settings.dict()
            for key, value in settings_dict.items():
                db_setting = db.query(Setting).filter_by(key=key).first()
                if db_setting:
                    db_setting.value = json.dumps(value)
                else:
                    db.add(Setting(key=key, value=json.dumps(value)))
            db.commit()

    def get_settings(self) -> Settings:
        return self.settings
