"""
Rotas da API - Tarefas
Implementa todas as operações CRUD para tarefas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional
from datetime import date, datetime
from app.core.database import get_db
from app.models import Tarefa
from app.schemas import (
    TarefaCreate, TarefaUpdate, TarefaResponse, TarefaFilters,
    PaginationParams, PaginationResponse, DataResponse
)
from app.services.auth import get_current_user
from app.services.progress import recalcular_progresso_habito

router = APIRouter(prefix="/tarefas", tags=["tarefas"])

@router.get("", response_model=DataResponse)
async def listar_tarefas(
    habito_id: Optional[str] = Query(None, description="Filtro por hábito"),
    busca: Optional[str] = Query(None, description="Busca em título e descrição"),
    status_kanban: Optional[List[str]] = Query(None, description="Filtro por status kanban"),
    prioridade: Optional[List[str]] = Query(None, description="Filtro por prioridade"),
    data_limite_inicio: Optional[date] = Query(None, description="Data limite início"),
    data_limite_fim: Optional[date] = Query(None, description="Data limite fim"),
    order_by: str = Query("created_at", description="Campo para ordenação"),
    order_dir: str = Query("desc", pattern=r"^(asc|desc)$", description="Direção da ordenação"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista tarefas do usuário com filtros e paginação"""
    
    # Query base
    query = db.query(Tarefa).filter(Tarefa.usuario_id == current_user["sub"])
    
    # Aplicar filtros
    if habito_id:
        query = query.filter(Tarefa.habito_id == habito_id)
    
    if busca:
        query = query.filter(
            or_(
                Tarefa.titulo.contains(busca),
                Tarefa.descricao.contains(busca)
            )
        )
    
    if status_kanban:
        query = query.filter(Tarefa.status_kanban.in_(status_kanban))
    
    if prioridade:
        query = query.filter(Tarefa.prioridade.in_(prioridade))
    
    if data_limite_inicio:
        query = query.filter(Tarefa.data_limite >= data_limite_inicio)
    
    if data_limite_fim:
        query = query.filter(Tarefa.data_limite <= data_limite_fim)
    
    # Total de registros
    total = query.count()
    
    # Ordenação
    order_column = getattr(Tarefa, order_by, Tarefa.created_at)
    if order_dir == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(asc(order_column))
    
    # Paginação
    offset = (page - 1) * limit
    tarefas = query.offset(offset).limit(limit).all()
    
    # Cálculo da paginação
    total_pages = (total + limit - 1) // limit
    
    pagination = PaginationResponse(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    tarefas_data = [t.__dict__ for t in tarefas]
    return DataResponse(data=tarefas_data, pagination=pagination)

@router.get("/{tarefa_id}", response_model=DataResponse)
async def obter_tarefa(
    tarefa_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém uma tarefa específica"""
    
    tarefa = db.query(Tarefa).filter(
        and_(
            Tarefa.id == tarefa_id,
            Tarefa.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    return DataResponse(data=tarefa.__dict__)

@router.post("", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
async def criar_tarefa(
    tarefa_data: TarefaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria uma nova tarefa"""
    
    # Criar nova tarefa
    nova_tarefa = Tarefa(
        usuario_id=current_user["sub"],
        **tarefa_data.model_dump()
    )
    
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    
    return DataResponse(data=nova_tarefa.__dict__)

@router.put("/{tarefa_id}", response_model=DataResponse)
async def atualizar_tarefa(
    tarefa_id: str,
    tarefa_data: TarefaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza uma tarefa existente"""
    
    tarefa = db.query(Tarefa).filter(
        and_(
            Tarefa.id == tarefa_id,
            Tarefa.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    # Verificar se status mudou para 'feito' para atualizar data_conclusao
    update_data = tarefa_data.model_dump(exclude_unset=True)
    
    if 'status_kanban' in update_data and update_data['status_kanban'] == 'feito':
        if tarefa.status_kanban != 'feito':  # Mudança para feito
            update_data['data_conclusao'] = datetime.utcnow()
    elif 'status_kanban' in update_data and update_data['status_kanban'] != 'feito':
        if tarefa.status_kanban == 'feito':  # Mudança de feito para outro status
            update_data['data_conclusao'] = None
    
    # Atualizar campos fornecidos
    for field, value in update_data.items():
        setattr(tarefa, field, value)
    
    db.commit()
    db.refresh(tarefa)
    
    # Recalcular progresso do hábito pai se necessário
    if tarefa.habito_id:
        recalcular_progresso_habito(db, tarefa.habito_id)
    
    return DataResponse(data=tarefa.__dict__)

@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_tarefa(
    tarefa_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove uma tarefa"""
    
    tarefa = db.query(Tarefa).filter(
        and_(
            Tarefa.id == tarefa_id,
            Tarefa.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    # Armazenar habito_id para recálculo
    habito_id = tarefa.habito_id
    
    # Remover tarefa
    db.delete(tarefa)
    db.commit()
    
    # Recalcular progresso do hábito pai se necessário
    if habito_id:
        recalcular_progresso_habito(db, habito_id)

@router.patch("/{tarefa_id}/status", response_model=DataResponse)
async def atualizar_status_tarefa(
    tarefa_id: str,
    status_kanban: str = Query(..., pattern=r"^(backlog|fazendo|feito)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza apenas o status kanban de uma tarefa"""
    
    tarefa = db.query(Tarefa).filter(
        and_(
            Tarefa.id == tarefa_id,
            Tarefa.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    # Atualizar status e data_conclusao se necessário
    old_status = tarefa.status_kanban
    tarefa.status_kanban = status_kanban
    
    if status_kanban == 'feito' and old_status != 'feito':
        tarefa.data_conclusao = datetime.utcnow()
    elif status_kanban != 'feito' and old_status == 'feito':
        tarefa.data_conclusao = None
    
    db.commit()
    db.refresh(tarefa)
    
    # Recalcular progresso do hábito pai se necessário
    if tarefa.habito_id:
        recalcular_progresso_habito(db, tarefa.habito_id)
    
    return DataResponse(data=tarefa.__dict__)

# Rota para listar tarefas por hábito
@router.get("/habito/{habito_id}", response_model=DataResponse)
async def listar_tarefas_por_habito(
    habito_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista tarefas de um hábito específico"""
    
    query = db.query(Tarefa).filter(
        and_(
            Tarefa.habito_id == habito_id,
            Tarefa.usuario_id == current_user["sub"]
        )
    )
    
    total = query.count()
    offset = (page - 1) * limit
    tarefas = query.offset(offset).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    pagination = PaginationResponse(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    tarefas_data = [t.__dict__ for t in tarefas]
    return DataResponse(data=tarefas_data, pagination=pagination)

# Rota para kanban - listar tarefas agrupadas por status
@router.get("/kanban/habito/{habito_id}", response_model=DataResponse)
async def listar_tarefas_kanban(
    habito_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista tarefas organizadas por status kanban (para visualização kanban)"""
    
    tarefas = db.query(Tarefa).filter(
        and_(
            Tarefa.habito_id == habito_id,
            Tarefa.usuario_id == current_user["sub"]
        )
    ).order_by(asc(Tarefa.posicao_kanban), desc(Tarefa.created_at)).all()
    
    # Agrupar por status
    kanban_data = {
        "backlog": [],
        "fazendo": [],
        "feito": []
    }
    
    for tarefa in tarefas:
        status = tarefa.status_kanban or "backlog"
        if status in kanban_data:
            kanban_data[status].append(tarefa.__dict__)
    
    return DataResponse(data=kanban_data)