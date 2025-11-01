"""
Schemas Pydantic - Usuários e Autenticação
"""
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

# Schemas para autenticação
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, max_length=200, description="Senha do usuário")

class UserRegister(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome completo")
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, max_length=200, description="Senha do usuário")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nome: str
    email: str
    avatar_url: Optional[str]
    preferencias: Optional[Dict[str, Any]]
    ativo: bool
    email_verificado: bool
    ultimo_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# Schema para atualização de perfil
class UserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    preferencias: Optional[Dict[str, Any]] = None

# Schema para dashboard
class DashboardResponse(BaseModel):
    total_objetivos: int = 0
    objetivos_ativos: int = 0
    total_habitos: int = 0
    habitos_ativos: int = 0
    total_tarefas: int = 0
    tarefas_concluidas: int = 0
    progresso_medio_objetivos: float = 0.0
    tarefas_atrasadas: int = 0