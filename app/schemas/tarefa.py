"""
Schemas Pydantic - Tarefas
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class StatusTarefa(str, Enum):
    BACKLOG = "backlog"
    A_FAZER = "a_fazer"
    FAZENDO = "fazendo"
    BLOQUEADA = "bloqueada"
    CONCLUIDA = "concluida"

class PrioridadeTarefa(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"

# Schemas para criação
class TarefaCreate(BaseModel):
    objetivo_id: Optional[str] = Field(None, description="ID do objetivo (opcional)")
    habito_id: Optional[str] = Field(None, description="ID do hábito (opcional)")
    titulo: str = Field(..., min_length=1, max_length=255, description="Título da tarefa")
    descricao: Optional[str] = Field(None, description="Descrição detalhada da tarefa")
    prioridade: Optional[PrioridadeTarefa] = Field(None, description="Prioridade da tarefa")
    status: StatusTarefa = Field(StatusTarefa.BACKLOG, description="Status da tarefa")
    estimativa_horas: Optional[Decimal] = Field(None, ge=0, description="Estimativa em horas")
    prazo: Optional[date] = Field(None, description="Data limite")
    tags: Optional[List[str]] = Field(None, description="Tags para categorização")
    anexos: Optional[List[str]] = Field(None, description="URLs de anexos")

# Schemas para atualização
class TarefaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    prioridade: Optional[PrioridadeTarefa] = None
    status: Optional[StatusTarefa] = None
    estimativa_horas: Optional[Decimal] = Field(None, ge=0)
    horas_gastas: Optional[Decimal] = Field(None, ge=0)
    prazo: Optional[date] = None
    progresso: Optional[Decimal] = Field(None, ge=0, le=100)
    posicao: Optional[int] = None
    tags: Optional[List[str]] = None
    anexos: Optional[List[str]] = None

# Schema de resposta
class TarefaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    usuario_id: str
    objetivo_id: Optional[str]
    habito_id: Optional[str]
    titulo: str
    descricao: Optional[str]
    prioridade: Optional[PrioridadeTarefa]
    status: StatusTarefa
    estimativa_horas: Optional[Decimal]
    horas_gastas: Decimal
    prazo: Optional[date]
    progresso: Decimal
    posicao: Optional[int]
    tags: Optional[List[str]]
    anexos: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

# Schema para listagem com informações relacionadas (usando view)
class TarefaCompleta(TarefaResponse):
    objetivo_titulo: Optional[str] = None
    objetivo_cor: Optional[str] = None
    habito_titulo: Optional[str] = None
    habito_frequencia: Optional[str] = None
    em_atraso: bool = False

# Schema para filtros
class TarefaFilters(BaseModel):
    objetivo_id: Optional[str] = Field(None, description="Filtro por objetivo")
    habito_id: Optional[str] = Field(None, description="Filtro por hábito")
    busca: Optional[str] = Field(None, description="Busca em título e descrição")
    status: Optional[List[StatusTarefa]] = Field(None, description="Filtro por status")
    prioridade: Optional[List[PrioridadeTarefa]] = Field(None, description="Filtro por prioridade")
    prazo_inicio: Optional[date] = Field(None, description="Prazo a partir de")
    prazo_fim: Optional[date] = Field(None, description="Prazo até")
    order_by: Optional[str] = Field("created_at", description="Campo para ordenação")
    order_dir: Optional[str] = Field("desc", pattern=r"^(asc|desc)$", description="Direção da ordenação")

# Schema para exclusão em lote
class TarefaDeleteBatch(BaseModel):
    ids: List[str] = Field(..., min_length=1, description="Lista de IDs para exclusão")