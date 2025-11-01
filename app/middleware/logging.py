"""
Middleware de logging para requisições HTTP
"""
import logging
import time
import json
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.logging_config import logging_settings
from app.models import Usuario
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Cache simples para informações do usuário (evita consultas frequentes ao BD)
_user_cache = {}
_cache_ttl = logging_settings.USER_CACHE_TTL

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra informações detalhadas de todas as requisições HTTP,
    incluindo dados do usuário quando disponível.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next):
        # Pular requisições OPTIONS (CORS preflight) para evitar conflitos
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # Verificar se a rota deve ser excluída do logging
        if request.url.path in logging_settings.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Capturar tempo de início
        start_time = time.time()
        
        # Extrair informações básicas da requisição
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Tentar extrair informações do usuário do token
        user_info = await self._extract_user_info(request)
        
        # Capturar corpo da requisição para métodos POST/PUT/PATCH
        body_info = await self._get_request_body_info(request) if logging_settings.LOG_REQUEST_BODY else "desabilitado"
        
        # Log da requisição de entrada
        emoji = logging_settings.LOG_EMOJIS["request"]
        user_emoji = logging_settings.LOG_EMOJIS["user_info"] if user_info else logging_settings.LOG_EMOJIS["anonymous"]
        
        logger.info(
            f"{emoji} REQUISIÇÃO RECEBIDA | "
            f"Método: {method} | "
            f"URL: {url} | "
            f"IP: {client_ip} | "
            f"User-Agent: {user_agent[:100]}..." if len(user_agent) > 100 else f"User-Agent: {user_agent} | "
            f"{user_emoji} Usuário: {self._format_user_info(user_info)} | "
            f"Body: {body_info}"
        )
        
        # Processar requisição
        try:
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = time.time() - start_time
            
            # Determinar emoji baseado no status da resposta
            if 200 <= response.status_code < 300:
                response_emoji = logging_settings.LOG_EMOJIS["response_success"]
            else:
                response_emoji = logging_settings.LOG_EMOJIS["response_error"]
            
            # Destacar requisições lentas
            time_info = f"{process_time:.3f}s"
            if logging_settings.ENABLE_PERFORMANCE_LOGS and process_time > logging_settings.SLOW_REQUEST_THRESHOLD:
                time_info = f"🐌 {time_info} (LENTA)"
            
            # Log da resposta
            logger.info(
                f"{response_emoji} RESPOSTA ENVIADA | "
                f"Status: {response.status_code} | "
                f"Tempo: {time_info} | "
                f"Método: {method} | "
                f"URL: {url} | "
                f"{user_emoji} Usuário: {self._format_user_info(user_info)}"
            )
            
            return response
            
        except Exception as e:
            # Calcular tempo até erro
            process_time = time.time() - start_time
            
            # Log do erro
            error_emoji = logging_settings.LOG_EMOJIS["error"]
            logger.error(
                f"{error_emoji} ERRO NA REQUISIÇÃO | "
                f"Erro: {str(e)} | "
                f"Tempo: {process_time:.3f}s | "
                f"Método: {method} | "
                f"URL: {url} | "
                f"{user_emoji} Usuário: {self._format_user_info(user_info)}"
            )
            
            raise
    
    async def _extract_user_info(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extrai informações do usuário do token JWT"""
        try:
            # Verificar se há token de autorização
            authorization = request.headers.get("authorization")
            if not authorization:
                logger.debug("🔍 Debug: Nenhum header Authorization encontrado")
                return None
            
            if not authorization.startswith("Bearer "):
                logger.debug(f"🔍 Debug: Header Authorization mal formatado: {authorization[:20]}...")
                return None
            
            # Extrair token
            token = authorization.split(" ")[1]
            logger.debug(f"🔍 Debug: Token extraído: {token[:20]}...")
            
            # Decodificar token
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            logger.debug(f"🔍 Debug: Payload decodificado: {payload}")
            
            user_id = payload.get("sub")
            if not user_id:
                logger.debug("🔍 Debug: Nenhum 'sub' encontrado no payload")
                return None
            
            # Verificar cache primeiro
            cache_key = f"user_{user_id}"
            now = datetime.utcnow()
            
            if cache_key in _user_cache:
                cached_data = _user_cache[cache_key]
                if now - cached_data["timestamp"] < _cache_ttl:
                    return cached_data["data"]
                else:
                    # Cache expirado, remover entrada
                    del _user_cache[cache_key]
            
            # Buscar informações do usuário no banco
            try:
                db_gen = get_db()
                db = next(db_gen)
                try:
                    user = db.query(Usuario).filter(Usuario.id == user_id).first()
                    if user:
                        user_data = {
                            "id": user.id,
                            "nome": user.nome,
                            "email": user.email,
                            "is_active": user.ativo
                        }
                        
                        logger.debug(f"🔍 Debug: Usuário encontrado no BD: {user.nome} ({user.email})")
                        
                        # Adicionar ao cache
                        _user_cache[cache_key] = {
                            "data": user_data,
                            "timestamp": now
                        }
                        
                        return user_data
                    else:
                        logger.debug(f"🔍 Debug: Usuário com ID {user_id} não encontrado no BD")
                finally:
                    db.close()
            except Exception as db_error:
                logger.warning(f"Erro ao buscar usuário no banco: {db_error}")
                # Retornar informações básicas do token
                fallback_data = {
                    "id": user_id,
                    "nome": "Desconhecido",
                    "email": "Desconhecido",
                    "is_active": True
                }
                
                # Cache também o fallback por um tempo menor
                _user_cache[cache_key] = {
                    "data": fallback_data,
                    "timestamp": now
                }
                
                return fallback_data
            
            return None
            
        except JWTError as jwt_error:
            logger.debug(f"🔍 Debug: Erro JWT: {jwt_error}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair informações do usuário: {e}")
            return None
    
    async def _get_request_body_info(self, request: Request) -> str:
        """Obtém informações resumidas do corpo da requisição"""
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                # Capturar corpo da requisição
                body = await request.body()
                
                if not body:
                    return "vazio"
                
                # Tentar decodificar como JSON
                try:
                    json_body = json.loads(body.decode('utf-8'))
                    
                    # Para dados sensíveis, não logar o conteúdo completo
                    if any(field in json_body for field in logging_settings.SENSITIVE_FIELDS):
                        return f"JSON com dados sensíveis ({len(body)} bytes)"
                    
                    # Limitar tamanho do log
                    body_str = json.dumps(json_body, ensure_ascii=False)
                    max_size = logging_settings.MAX_BODY_SIZE_LOG
                    if len(body_str) > max_size:
                        return f"JSON ({len(body)} bytes): {body_str[:max_size]}..."
                    
                    return f"JSON: {body_str}"
                    
                except json.JSONDecodeError:
                    # Não é JSON, retornar informação básica
                    return f"não-JSON ({len(body)} bytes)"
            
            return "não aplicável"
            
        except Exception as e:
            logger.warning(f"Erro ao processar corpo da requisição: {e}")
            return "erro ao processar"
    
    def _format_user_info(self, user_info: Optional[Dict[str, Any]]) -> str:
        """Formata informações do usuário para o log"""
        if not user_info:
            return "Anônimo"
        
        return (
            f"ID:{user_info.get('id', 'N/A')} | "
            f"Nome:{user_info.get('nome', 'N/A')} | "
            f"Email:{user_info.get('email', 'N/A')} | "
            f"Ativo:{user_info.get('is_active', 'N/A')}"
        )