"""
Configurações da aplicação GoalManager Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Configurações da API
    app_name: str = "GoalManager API"
    version: str = "1.0.0"
    description: str = "API para gerenciamento de objetivos, hábitos e tarefas"
    debug: bool = False
    
    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = 3000
    reload: bool = False
    
    # Configurações do banco de dados
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "goalmanager_user"
    mysql_password: str = "goalmanager_pass123"
    mysql_database: str = "goalmanager"
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    # Configurações JWT
    jwt_secret_key: str = "goalmanager_super_secret_key_change_in_production_123456789"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    
    # Configurações de CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "*"  # Permitir qualquer origem durante desenvolvimento
    ]
    
    # Configurações de paginação
    default_page_size: int = 50
    max_page_size: int = 100
    
    # Configurações de rate limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 60  # segundos
    
    # Configurações de timezone
    timezone: str = "UTC"
    
    # Configurações de desenvolvimento
    disable_auth: bool = False  # Para desabilitar autenticação em desenvolvimento
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Permite valores extras do .env

# Instância global das configurações
settings = Settings()