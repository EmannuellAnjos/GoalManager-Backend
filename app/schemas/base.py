"""
Schemas Pydantic para validação de dados - Base
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# Esquemas base para paginação
class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 50

class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

# Esquema base para resposta da API
class BaseResponse(BaseModel):
    message: str = "Success"

class DataResponse(BaseModel):
    data: dict | list
    pagination: Optional[PaginationResponse] = None