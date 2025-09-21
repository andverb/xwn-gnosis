from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_set = Column(String(50), nullable=False)
    tags = Column(JSON, nullable=True)  # searchable tags like ["combat", "spells", "d20"]
    # mechanics = Column(JSON, nullable=True)  #TODO language-agnostic game mechanics
    translations = Column(JSON, nullable=False)  # multilingual content
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
