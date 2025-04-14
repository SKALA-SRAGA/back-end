from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)

    script = relationship(
        "Script",
        cascade="all, delete-orphan",
        lazy="dynamic"  # ✅ 비동기 처리를 위해 lazy="selectin" 사용
    )

    receipt = relationship(
        "Receipt",
        cascade="all, delete-orphan",
        lazy="dynamic"  # ✅ 비동기 처리를 위해 lazy="selectin" 사용
    )

