import app.db.entity.user
import app.db.entity.script
import app.db.entity.receipt
import logging
from app.db.database import Base

logging.info("Registered tables: %s", list(Base.metadata.tables.keys()))