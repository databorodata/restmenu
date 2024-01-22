from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    submenus = relationship("Submenu", back_populates="menu", cascade="all, delete")
    dishes = relationship("Dish", back_populates="menu", cascade="all, delete")

class Submenu(Base):
    __tablename__ = 'submenu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menu.id', ondelete="CASCADE"))
    menu = relationship("Menu", back_populates="submenus")
    dishes = relationship("Dish", back_populates="submenu", cascade="all, delete")

class Dish(Base):
    __tablename__ = 'dish'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(String, nullable=False)
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenu.id', ondelete="CASCADE"))
    submenu = relationship("Submenu", back_populates="dishes")
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menu.id', ondelete="CASCADE"))
    menu = relationship("Menu", back_populates="dishes")
