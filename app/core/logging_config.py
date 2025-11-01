"""
Configurações específicas para o sistema de logging
"""
from datetime import timedelta

class LoggingSettings:
    """Configurações do middleware de logging"""
    
    # Cache de informações do usuário
    USER_CACHE_TTL = timedelta(minutes=5)
    USER_CACHE_MAX_SIZE = 1000  # Máximo de usuários no cache
    
    # Controle de logging
    LOG_REQUEST_BODY = True  # Se deve logar o corpo das requisições
    LOG_RESPONSE_BODY = False  # Se deve logar o corpo das respostas
    MAX_BODY_SIZE_LOG = 200  # Tamanho máximo do body para log (caracteres)
    
    # Rotas excluídas do logging (para reduzir verbosidade)
    EXCLUDED_PATHS = {
        "/health",
        "/api/v1/dashboard/health",
        "/favicon.ico",
        "/robots.txt"
    }
    
    # Campos sensíveis que não devem aparecer nos logs
    SENSITIVE_FIELDS = {
        "password",
        "senha",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "key",
        "authorization"
    }
    
    # Headers que devem ser incluídos no log
    LOGGED_HEADERS = {
        "user-agent",
        "referer",
        "x-forwarded-for",
        "x-real-ip",
        "content-type",
        "accept"
    }
    
    # Formatação de logs
    LOG_EMOJIS = {
        "request": "🌐",
        "response_success": "✅", 
        "response_error": "❌",
        "user_info": "👤",
        "anonymous": "🔒",
        "warning": "⚠️",
        "error": "💥"
    }
    
    # Performance
    ENABLE_PERFORMANCE_LOGS = True  # Se deve logar tempo de resposta
    SLOW_REQUEST_THRESHOLD = 1.0  # Segundos - requisições mais lentas que isso são destacadas
    
    # Níveis de detalhamento
    class LogLevel:
        MINIMAL = "minimal"      # Apenas método, URL e usuário
        STANDARD = "standard"    # Informações básicas + tempo + status
        DETAILED = "detailed"    # Tudo incluído + headers + body
        DEBUG = "debug"          # Máximo detalhamento + cache info
    
    CURRENT_LOG_LEVEL = LogLevel.STANDARD

# Instância global das configurações de logging
logging_settings = LoggingSettings()