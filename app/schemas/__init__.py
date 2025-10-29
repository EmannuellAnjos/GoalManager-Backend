"""
Inicialização dos schemas
"""
from .base import PaginationParams, PaginationResponse, BaseResponse, DataResponse
from .auth import UserLogin, UserRegister, TokenResponse, UserResponse, UserUpdate, DashboardResponse
from .objetivo import ObjetivoCreate, ObjetivoUpdate, ObjetivoResponse, ObjetivoComEstatisticas, ObjetivoFilters, StatusObjetivo
from .habito import HabitoCreate, HabitoUpdate, HabitoResponse, MarcarHabitoFeito, HabitoFilters, StatusHabito, FrequenciaHabito
from .tarefa import TarefaCreate, TarefaUpdate, TarefaResponse, TarefaCompleta, TarefaFilters, TarefaDeleteBatch, StatusTarefa, PrioridadeTarefa

__all__ = [
    # Base
    "PaginationParams",
    "PaginationResponse", 
    "BaseResponse",
    "DataResponse",
    # Auth
    "UserLogin",
    "UserRegister",
    "TokenResponse",
    "UserResponse",
    "UserUpdate",
    "DashboardResponse",
    # Objetivo
    "ObjetivoCreate",
    "ObjetivoUpdate",
    "ObjetivoResponse",
    "ObjetivoComEstatisticas",
    "ObjetivoFilters",
    "StatusObjetivo",
    # Habito
    "HabitoCreate",
    "HabitoUpdate",
    "HabitoResponse",
    "MarcarHabitoFeito",
    "HabitoFilters",
    "StatusHabito",
    "FrequenciaHabito",
    # Tarefa
    "TarefaCreate",
    "TarefaUpdate",
    "TarefaResponse",
    "TarefaCompleta",
    "TarefaFilters",
    "TarefaDeleteBatch",
    "StatusTarefa",
    "PrioridadeTarefa"
]