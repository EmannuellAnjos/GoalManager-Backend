"""
Schemas Pydantic - Hábitos
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class StatusHabito(str, Enum):
    ATIVO = "ativo"
    PAUSADO = "pausado"
    CONCLUIDO = "concluido"

class FrequenciaHabito(str, Enum):
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"

# Schemas para criação
class HabitoCreate(BaseModel):
    objetivo_id: str = Field(..., description="ID do objetivo pai")
    titulo: str = Field(..., min_length=1, max_length=255, description="Título do hábito")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do hábito")
    frequencia: FrequenciaHabito = Field(..., description="Frequência do hábito")
    alvo_por_periodo: int = Field(..., ge=1, description="Meta de realizações por período")
    status: StatusHabito = Field(StatusHabito.ATIVO, description="Status do hábito")
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em hexadecimal")
    icone: Optional[str] = Field(None, max_length=50, description="Nome do ícone")

# Schemas para atualização
class HabitoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    frequencia: Optional[FrequenciaHabito] = None
    alvo_por_periodo: Optional[int] = Field(None, ge=1)
    realizados_no_periodo: Optional[int] = Field(None, ge=0)
    status: Optional[StatusHabito] = None
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icone: Optional[str] = Field(None, max_length=50)

# Schema de resposta
class HabitoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    usuario_id: str
    objetivo_id: str
    titulo: str
    descricao: Optional[str]
    frequencia: FrequenciaHabito
    alvo_por_periodo: int
    realizados_no_periodo: int
    status: StatusHabito
    progresso: Decimal
    periodo_inicio: Optional[date]
    cor: Optional[str]
    icone: Optional[str]
    created_at: datetime
    updated_at: datetime

# Schema para marcar como feito
class MarcarHabitoFeito(BaseModel):
    data_realizacao: Optional[date] = Field(None, description="Data da realização (padrão: hoje)")
    quantidade: int = Field(1, ge=1, description="Quantidade de realizações")
    observacoes: Optional[str] = Field(None, description="Observações sobre a realização")

# Schema para filtros
class HabitoFilters(BaseModel):
    objetivo_id: Optional[str] = Field(None, description="Filtro por objetivo")
    busca: Optional[str] = Field(None, description="Busca em título e descrição")
    status: Optional[list[StatusHabito]] = Field(None, description="Filtro por status")
    frequencia: Optional[list[FrequenciaHabito]] = Field(None, description="Filtro por frequência")
    order_by: Optional[str] = Field("created_at", description="Campo para ordenação")
    order_dir: Optional[str] = Field("desc", pattern=r"^(asc|desc)$", description="Direção da ordenação")