"""
Modelos SQLAlchemy - Tarefas
"""
from sqlalchemy import Column, String, Text, Numeric, DateTime, Date, Integer, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Tarefa(Base):
    __tablename__ = "tarefas"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), nullable=False, index=True)
    # objetivo_id removido - tarefas agora são ligadas apenas a hábitos
    habito_id = Column(String(36), nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    prioridade = Column(String(10), nullable=True, index=True)  # baixa, media, alta
    status = Column(String(20), nullable=False, default='backlog', index=True)  # backlog, a_fazer, fazendo, bloqueada, concluida
    estimativa_horas = Column(Numeric(6, 2), nullable=True)
    horas_gastas = Column(Numeric(6, 2), default=0.00, nullable=False)
    prazo = Column(Date, nullable=True, index=True)
    progresso = Column(Numeric(5, 2), default=0.00, nullable=False, index=True)
    posicao = Column(Integer, nullable=True, index=True)  # Posição para ordenação personalizada
    tags = Column(JSON, nullable=True)  # Array de tags para categorização
    anexos = Column(JSON, nullable=True)  # Array de URLs de anexos
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)