"""
Serviço de autenticação - Middleware e dependências
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import settings
from app.models import Usuario
from typing import Dict, Optional

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Dependency que verifica o token JWT e retorna dados do usuário atual
    """
    from app.core.config import settings
    
    # Se autenticação estiver desabilitada, retorna usuário mock
    if settings.disable_auth:
        return {
            "sub": "demo-user-123", 
            "email": "demo@goalmanager.com", 
            "nome": "Usuário Demo"
        }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso obrigatório"
        )
    
    try:
        # Verificar token
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Verificar se usuário existe e está ativo
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user or not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )
        
        return {"sub": user_id, "email": user.email, "nome": user.nome}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na autenticação"
        )

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def hash_password(password: str) -> str:
    """Alias para get_password_hash"""
    return get_password_hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verifica e decodifica um token JWT"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """Autentica um usuário com email e senha"""
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.senha_hash):
        return None
    
    # Atualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency que retorna usuário ativo
    """
    return current_user