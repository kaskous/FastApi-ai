from sqlalchemy import Column, Integer, String, Text
from app.db import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    format = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
