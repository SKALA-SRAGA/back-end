from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from app.db.database import Base

class Script(Base):
    __tablename__ = "script"

    id = Column(String(30), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    name = Column(String(30), nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    file_path = Column(String(255), nullable=False)