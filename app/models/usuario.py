"""
Modelos SQLAlchemy - Usuários
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    preferencias = Column(JSON, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    email_verificado = Column(Boolean, default=False, nullable=False)
    ultimo_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class TokenAuth(Base):
    __tablename__ = "tokens_auth"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)  # access, refresh, reset_password, verify_email
    expires_at = Column(DateTime, nullable=False, index=True)
    usado = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)