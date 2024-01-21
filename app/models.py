from sqlalchemy import Column, Integer, String, Float, ForeignKey
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
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menu.id'))
    menu = relationship("Menu", back_populates="submenus")
    dishes = relationship("Dish", back_populates="submenu", cascade="all, delete")

class Dish(Base):
    __tablename__ = 'dish'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=True, default=0.0)
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenu.id'))
    submenu = relationship("Submenu", back_populates="dishes")
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menu.id'))
    menu = relationship("Menu", back_populates="dishes")