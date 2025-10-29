"""
Modelos SQLAlchemy - Hábitos
"""
from sqlalchemy import Column, String, Text, Integer, Numeric, Enum, DateTime, Date
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Habito(Base):
    __tablename__ = "habitos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), nullable=False, index=True)
    objetivo_id = Column(String(36), nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    frequencia = Column(String(20), nullable=False, index=True)  # diario, semanal, mensal
    alvo_por_periodo = Column(Integer, nullable=False)
    realizados_no_periodo = Column(Integer, default=0, nullable=False)
    status = Column(String(20), nullable=False, default='ativo', index=True)  # ativo, pausado, concluido
    progresso = Column(Numeric(5, 2), default=0.00, nullable=False, index=True)
    periodo_inicio = Column(Date, nullable=True)  # Início do período atual de contagem
    cor = Column(String(7), nullable=True)
    icone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class HabitoRealizacao(Base):
    __tablename__ = "habito_realizacoes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    habito_id = Column(String(36), nullable=False, index=True)
    usuario_id = Column(String(36), nullable=False, index=True)
    data_realizacao = Column(Date, nullable=False, index=True)
    quantidade = Column(Integer, default=1, nullable=False)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)