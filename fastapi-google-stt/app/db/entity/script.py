from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Script(Base):
    __tablename__ = "script"

    id = Column(String(30), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    file_path = Column(String(255), nullable=False)