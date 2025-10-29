"""
Modelos SQLAlchemy - Auditoria
"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), nullable=False, index=True)
    tabela = Column(String(50), nullable=False, index=True)
    registro_id = Column(String(36), nullable=False, index=True)
    acao = Column(String(10), nullable=False, index=True)  # CREATE, UPDATE, DELETE
    dados_antigos = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)