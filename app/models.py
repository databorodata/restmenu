from sqlalchemy import Table, Column, Integer, String, MetaData, Float
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

metadata = MetaData()


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    submenus_count = Column(Float, nullable=True, default=0.0)
    dishes_count = Column(Integer, nullable=True, default=0)


class Submenu(Base):
    __tablename__ = 'submenu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    dishes_count = Column(Integer, nullable=True, default=0)

class Dish(Base):
    __tablename__ = 'dish'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=True, default=0.0)

# menu = Table(
#     "menu",
#     metadata,
#     Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
#     Column("title", String),
#     Column("description", String),
#     Column("submenus_count", Float, nullable=True),
#     Column("dishes_count", Integer),
# )