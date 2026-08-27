from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    current_city: Mapped[str] = mapped_column(String(120))
    destination_city: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(120))
    move_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    move_type: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(String(120))
    profile = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    applications = relationship('Application', back_populates='user', cascade='all, delete-orphan')

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    vehicle: Mapped[bool] = mapped_column(Boolean, default=False)
    voter: Mapped[bool] = mapped_column(Boolean, default=False)
    benefits: Mapped[bool] = mapped_column(Boolean, default=False)
    student: Mapped[bool] = mapped_column(Boolean, default=False)
    property: Mapped[bool] = mapped_column(Boolean, default=False)
    user = relationship('User', back_populates='profile')

class GovernmentService(Base):
    __tablename__ = 'government_services'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    service_name: Mapped[str] = mapped_column(String(200))
    department: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    trigger_conditions: Mapped[str] = mapped_column(Text)
    applicability: Mapped[str] = mapped_column(String(60))
    priority: Mapped[str] = mapped_column(String(30))
    why_relevant: Mapped[str] = mapped_column(Text)
    process: Mapped[str] = mapped_column(Text)
    official_url: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text)
    source_last_verified: Mapped[date | None] = mapped_column(Date, nullable=True)
    requirements = relationship('ServiceRequirement', back_populates='service', cascade='all, delete-orphan')
    dependencies = relationship('ServiceDependency', foreign_keys='ServiceDependency.service_id', back_populates='service', cascade='all, delete-orphan')
    sources = relationship('Source', back_populates='service', cascade='all, delete-orphan')

class ServiceRequirement(Base):
    __tablename__ = 'service_requirements'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey('government_services.id'))
    requirement: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    service = relationship('GovernmentService', back_populates='requirements')

class ServiceDependency(Base):
    __tablename__ = 'service_dependencies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey('government_services.id'))
    dependency_service_id: Mapped[str] = mapped_column(String(60))
    dependency_description: Mapped[str] = mapped_column(Text)
    service = relationship('GovernmentService', foreign_keys=[service_id], back_populates='dependencies')

class Application(Base):
    __tablename__ = 'applications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('government_services.id'))
    status: Mapped[str] = mapped_column(String(40), default='Not Started')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship('User', back_populates='applications')
    service = relationship('GovernmentService')

class Source(Base):
    __tablename__ = 'sources'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey('government_services.id'))
    source_name: Mapped[str] = mapped_column(String(200))
    source_url: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(60))
    verified_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    service = relationship('GovernmentService', back_populates='sources')
