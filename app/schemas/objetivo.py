"""
Schemas Pydantic - Objetivos
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

def to_camel(string: str) -> str:
    """Converte snake_case para camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class StatusObjetivo(str, Enum):
    PLANEJADO = "planejado"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    ARQUIVADO = "arquivado"

# Schemas para criação
class ObjetivoCreate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra='ignore'
    )
    
    titulo: str = Field(..., min_length=1, max_length=255, description="Título do objetivo")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do objetivo")
    inicio: Optional[date] = Field(None, description="Data de início")
    fim: Optional[date] = Field(None, description="Data de fim")
    status: StatusObjetivo = Field(StatusObjetivo.PLANEJADO, description="Status do objetivo")
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em hexadecimal")
    icone: Optional[str] = Field(None, max_length=50, description="Nome do ícone")

# Schemas para atualização
class ObjetivoUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra='ignore'
    )
    
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    inicio: Optional[date] = None
    fim: Optional[date] = None
    status: Optional[StatusObjetivo] = None
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icone: Optional[str] = Field(None, max_length=50)

# Schema de resposta
class ObjetivoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
    
    id: str
    usuario_id: str
    titulo: str
    descricao: Optional[str]
    inicio: Optional[date]
    fim: Optional[date]
    status: StatusObjetivo
    progresso: Decimal
    cor: Optional[str]
    icone: Optional[str]
    created_at: datetime
    updated_at: datetime

# Schema para listagem com estatísticas (usando view)
class ObjetivoComEstatisticas(ObjetivoResponse):
    total_habitos: int = 0
    habitos_ativos: int = 0
    total_tarefas: int = 0
    tarefas_concluidas: int = 0
    progresso_medio_habitos: Decimal = Decimal('0.00')
    progresso_medio_tarefas: Decimal = Decimal('0.00')

# Schema para filtros
class ObjetivoFilters(BaseModel):
    busca: Optional[str] = Field(None, description="Busca em título e descrição")
    status: Optional[list[StatusObjetivo]] = Field(None, description="Filtro por status")
    inicio: Optional[date] = Field(None, description="Data início mínima")
    fim: Optional[date] = Field(None, description="Data fim máxima")
    order_by: Optional[str] = Field("created_at", description="Campo para ordenação")
    order_dir: Optional[str] = Field("desc", pattern=r"^(asc|desc)$", description="Direção da ordenação")