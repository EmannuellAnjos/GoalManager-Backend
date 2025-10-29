"""
Modelos SQLAlchemy - Objetivos
"""
from sqlalchemy import Column, String, Text, Date, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Objetivo(Base):
    __tablename__ = "objetivos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    inicio = Column(Date, nullable=True)
    fim = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default='planejado', index=True)  # planejado, em_andamento, concluido, arquivado
    progresso = Column(Numeric(5, 2), default=0.00, nullable=False, index=True)
    cor = Column(String(7), nullable=True)  # Cor em hexadecimal (#RRGGBB)
    icone = Column(String(50), nullable=True)  # Nome do ícone
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)