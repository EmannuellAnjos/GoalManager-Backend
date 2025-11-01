"""
Rotas da API - Autenticação e Dashboard
Implementa autenticação, registro e dashboard do usuário
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import Usuario, Objetivo, Habito, Tarefa, HabitoRealizacao
from app.schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    DataResponse, DashboardResponse
)
from app.services.auth import (
    authenticate_user, create_access_token, hash_password,
    get_current_user, get_password_hash, verify_password
)

# Routers separados para organização
auth_router = APIRouter(prefix="/auth", tags=["autenticação"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])
user_router = APIRouter(prefix="/user", tags=["usuário"])

# === ROTAS DE AUTENTICAÇÃO ===

@auth_router.post("/register", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Registra um novo usuário"""
    
    # Verificar se email já existe
    existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    hashed_password = hash_password(user_data.password)
    novo_usuario = Usuario(
        nome=user_data.nome,
        email=user_data.email,
        senha_hash=hashed_password,
        ativo=True
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    # Gerar token de acesso
    access_token = create_access_token(data={"sub": novo_usuario.id})
    
    return DataResponse(data={
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": novo_usuario.id,
            "nome": novo_usuario.nome,
            "email": novo_usuario.email,
            "is_active": novo_usuario.ativo,
            "created_at": novo_usuario.created_at
        }
    })

@auth_router.post("/login", response_model=DataResponse)
async def login_usuario(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Autentica usuário e retorna token"""
    
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gerar token de acesso
    access_token = create_access_token(data={"sub": user.id})
    
    return DataResponse(data={
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "is_active": user.ativo,
            "last_login": user.ultimo_login
        }
    })

@auth_router.post("/refresh", response_model=DataResponse)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """Renova o token de acesso"""
    
    new_token = create_access_token(data={"sub": current_user["sub"]})
    
    return DataResponse(data={
        "access_token": new_token,
        "token_type": "bearer"
    })

@auth_router.post("/logout", response_model=DataResponse)
async def logout_usuario(
    current_user = Depends(get_current_user)
):
    """Logout do usuário (principalmente para limpeza no frontend)"""
    
    return DataResponse(data={
        "message": "Logout realizado com sucesso"
    })

# === ROTAS DO USUÁRIO ===

@user_router.get("/profile", response_model=DataResponse)
async def obter_perfil(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém o perfil do usuário atual"""
    
    usuario = db.query(Usuario).filter(Usuario.id == current_user["sub"]).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return DataResponse(data={
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "is_active": usuario.ativo,
        "created_at": usuario.created_at,
        "last_login": usuario.ultimo_login
    })

@user_router.put("/profile", response_model=DataResponse)
async def atualizar_perfil(
    update_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza o perfil do usuário"""
    
    usuario = db.query(Usuario).filter(Usuario.id == current_user["sub"]).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Campos permitidos para atualização
    allowed_fields = ['nome']
    
    for field, value in update_data.items():
        if field in allowed_fields and value is not None:
            setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return DataResponse(data={
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "is_active": usuario.ativo,
        "updated_at": usuario.updated_at
    })

@user_router.post("/change-password", response_model=DataResponse)
async def alterar_senha(
    passwords: Dict[str, str],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Altera a senha do usuário"""
    
    current_password = passwords.get("current_password")
    new_password = passwords.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual e nova senha são obrigatórias"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == current_user["sub"]).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar senha atual
    if not verify_password(current_password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Atualizar senha
    usuario.senha_hash = get_password_hash(new_password)
    db.commit()
    
    return DataResponse(data={
        "message": "Senha alterada com sucesso"
    })

# === ROTAS DO DASHBOARD ===

@dashboard_router.get("/stats", response_model=DataResponse)
async def obter_estatisticas(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém estatísticas do dashboard do usuário"""
    
    user_id = current_user["sub"]
    
    # Contadores principais
    total_objetivos = db.query(func.count(Objetivo.id)).filter(Objetivo.usuario_id == user_id).scalar()
    total_habitos = db.query(func.count(Habito.id)).filter(Habito.usuario_id == user_id).scalar()
    total_tarefas = db.query(func.count(Tarefa.id)).filter(Tarefa.usuario_id == user_id).scalar()
    
    # Objetivos por status
    objetivos_ativos = db.query(func.count(Objetivo.id)).filter(
        Objetivo.usuario_id == user_id,
        Objetivo.status == 'ativo'
    ).scalar()
    
    objetivos_concluidos = db.query(func.count(Objetivo.id)).filter(
        Objetivo.usuario_id == user_id,
        Objetivo.status == 'concluido'
    ).scalar()
    
    # Hábitos por status
    habitos_ativos = db.query(func.count(Habito.id)).filter(
        Habito.usuario_id == user_id,
        Habito.status == 'ativo'
    ).scalar()
    
    # Tarefas por status kanban
    tarefas_backlog = db.query(func.count(Tarefa.id)).filter(
        Tarefa.usuario_id == user_id,
        Tarefa.status_kanban == 'backlog'
    ).scalar()
    
    tarefas_fazendo = db.query(func.count(Tarefa.id)).filter(
        Tarefa.usuario_id == user_id,
        Tarefa.status_kanban == 'fazendo'
    ).scalar()
    
    tarefas_feitas = db.query(func.count(Tarefa.id)).filter(
        Tarefa.usuario_id == user_id,
        Tarefa.status_kanban == 'feito'
    ).scalar()
    
    # Progresso médio dos objetivos
    avg_progresso_objetivos = db.query(func.avg(Objetivo.progresso)).filter(
        Objetivo.usuario_id == user_id,
        Objetivo.status == 'ativo'
    ).scalar() or 0
    
    # Progresso médio dos hábitos
    avg_progresso_habitos = db.query(func.avg(Habito.progresso)).filter(
        Habito.usuario_id == user_id,
        Habito.status == 'ativo'
    ).scalar() or 0
    
    # Realizações da semana (últimos 7 dias)
    data_limite = datetime.utcnow() - timedelta(days=7)
    realizacoes_semana = db.query(func.count(HabitoRealizacao.id)).filter(
        HabitoRealizacao.usuario_id == user_id,
        HabitoRealizacao.created_at >= data_limite
    ).scalar()
    
    return DataResponse(data={
        "totais": {
            "objetivos": total_objetivos,
            "habitos": total_habitos,
            "tarefas": total_tarefas
        },
        "objetivos": {
            "ativos": objetivos_ativos,
            "concluidos": objetivos_concluidos,
            "progresso_medio": float(avg_progresso_objetivos)
        },
        "habitos": {
            "ativos": habitos_ativos,
            "progresso_medio": float(avg_progresso_habitos)
        },
        "tarefas": {
            "backlog": tarefas_backlog,
            "fazendo": tarefas_fazendo,
            "feitas": tarefas_feitas
        },
        "atividade": {
            "realizacoes_ultima_semana": realizacoes_semana
        }
    })

@dashboard_router.get("/recent-activity", response_model=DataResponse)
async def obter_atividade_recente(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém atividades recentes do usuário"""
    
    user_id = current_user["sub"]
    
    # Realizações recentes de hábitos
    realizacoes_recentes = db.query(HabitoRealizacao).filter(
        HabitoRealizacao.usuario_id == user_id
    ).order_by(HabitoRealizacao.created_at.desc()).limit(limit).all()
    
    atividades = []
    for realizacao in realizacoes_recentes:
        # Buscar dados do hábito
        habito = db.query(Habito).filter(Habito.id == realizacao.habito_id).first()
        if habito:
            atividades.append({
                "tipo": "habito_realizado",
                "data": realizacao.created_at,
                "descricao": f"Completou hábito: {habito.titulo}",
                "entidade": {
                    "id": habito.id,
                    "titulo": habito.titulo,
                    "tipo": "habito"
                }
            })
    
    return DataResponse(data=atividades)

# === ROTAS DE UTILIDADE ===

@dashboard_router.get("/health", response_model=DataResponse)
async def health_check():
    """Verificação de saúde da API"""
    return DataResponse(data={
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    })