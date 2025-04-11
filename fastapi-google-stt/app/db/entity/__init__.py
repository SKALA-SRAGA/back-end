import app.db.entity.user
import app.db.entity.script
import logging
from app.db.database import Base

logging.info("Registered tables: %s", list(Base.metadata.tables.keys()))