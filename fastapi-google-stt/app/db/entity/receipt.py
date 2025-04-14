from sqlalchemy import Column, Integer, String, ForeignKey

from app.db.database import Base

class Receipt(Base):
    __tablename__ = "receipt"

    id = Column(String(30), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    name = Column(String(30), nullable=False)
    file_path = Column(String(255), nullable=False)