"""
Rotas da API - Hábitos
Implementa todas as operações CRUD para hábitos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional
from datetime import date, datetime
from app.core.database import get_db
from app.models import Habito, HabitoRealizacao
from app.schemas import (
    HabitoCreate, HabitoUpdate, HabitoResponse, MarcarHabitoFeito,
    HabitoFilters, PaginationParams, PaginationResponse, DataResponse
)
from app.services.auth import get_current_user
from app.services.progress import recalcular_progresso_habito, marcar_habito_feito, resetar_ciclo_habito
from app.utils.serialization import serialize_model, serialize_models

router = APIRouter(prefix="/habitos", tags=["habitos"])

@router.get("", response_model=DataResponse)
async def listar_habitos(
    objetivo_id: Optional[str] = Query(None, description="Filtro por objetivo"),
    busca: Optional[str] = Query(None, description="Busca em título e descrição"),
    status: Optional[List[str]] = Query(None, description="Filtro por status"),
    frequencia: Optional[List[str]] = Query(None, description="Filtro por frequência"),
    order_by: str = Query("created_at", description="Campo para ordenação"),
    order_dir: str = Query("desc", pattern=r"^(asc|desc)$", description="Direção da ordenação"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista hábitos do usuário com filtros e paginação"""
    
    # Query base
    query = db.query(Habito).filter(Habito.usuario_id == current_user["sub"])
    
    # Aplicar filtros
    if objetivo_id:
        query = query.filter(Habito.objetivo_id == objetivo_id)
    
    if busca:
        query = query.filter(
            or_(
                Habito.titulo.contains(busca),
                Habito.descricao.contains(busca)
            )
        )
    
    if status:
        query = query.filter(Habito.status.in_(status))
    
    if frequencia:
        query = query.filter(Habito.frequencia.in_(frequencia))
    
    # Total de registros
    total = query.count()
    
    # Ordenação
    order_column = getattr(Habito, order_by, Habito.created_at)
    if order_dir == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(asc(order_column))
    
    # Paginação
    offset = (page - 1) * limit
    habitos = query.offset(offset).limit(limit).all()
    
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
    
    habitos_data = serialize_models(habitos)
    return DataResponse(data=habitos_data, pagination=pagination)

@router.get("/{habito_id}", response_model=DataResponse)
async def obter_habito(
    habito_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém um hábito específico"""
    
    habito = db.query(Habito).filter(
        and_(
            Habito.id == habito_id,
            Habito.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito não encontrado"
        )
    
    return DataResponse(data=serialize_model(habito))

@router.post("", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
async def criar_habito(
    habito_data: HabitoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria um novo hábito"""
    
    # Criar novo hábito
    novo_habito = Habito(
        usuario_id=current_user["sub"],
        **habito_data.model_dump()
    )
    
    db.add(novo_habito)
    db.commit()
    db.refresh(novo_habito)
    
    return DataResponse(data=serialize_model(novo_habito))

@router.put("/{habito_id}", response_model=DataResponse)
async def atualizar_habito(
    habito_id: str,
    habito_data: HabitoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza um hábito existente"""
    
    habito = db.query(Habito).filter(
        and_(
            Habito.id == habito_id,
            Habito.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = habito_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habito, field, value)
    
    db.commit()
    db.refresh(habito)
    
    # Recalcular progresso se necessário
    recalcular_progresso_habito(db, habito_id)
    
    return DataResponse(data=serialize_model(habito))

@router.delete("/{habito_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_habito(
    habito_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove um hábito"""
    
    habito = db.query(Habito).filter(
        and_(
            Habito.id == habito_id,
            Habito.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito não encontrado"
        )
    
    # Remover realizações relacionadas
    db.query(HabitoRealizacao).filter(HabitoRealizacao.habito_id == habito_id).delete()
    
    # Remover hábito
    db.delete(habito)
    db.commit()

@router.post("/{habito_id}/marcar-feito", response_model=DataResponse)
async def marcar_habito_como_feito(
    habito_id: str,
    dados: MarcarHabitoFeito,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Incrementa contador de realizações do hábito"""
    
    data_realizacao = dados.data_realizacao or date.today()
    
    # Verificar se hábito existe e pertence ao usuário
    habito = db.query(Habito).filter(
        and_(
            Habito.id == habito_id,
            Habito.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito não encontrado"
        )
    
    # Registrar realização
    realizacao = HabitoRealizacao(
        habito_id=habito_id,
        usuario_id=current_user["sub"],
        data_realizacao=data_realizacao,
        quantidade=dados.quantidade,
        observacoes=dados.observacoes
    )
    
    db.add(realizacao)
    
    # Marcar como feito
    success = marcar_habito_feito(
        db, habito_id, current_user["sub"], 
        str(data_realizacao), dados.quantidade
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao marcar hábito como feito"
        )
    
    # Buscar hábito atualizado
    db.refresh(habito)
    
    return DataResponse(data={
        "id": habito.id,
        "realizados_no_periodo": habito.realizados_no_periodo,
        "progresso": float(habito.progresso),
        "updated_at": habito.updated_at
    })

@router.post("/{habito_id}/reset-ciclo", response_model=DataResponse)
async def resetar_ciclo_habito_endpoint(
    habito_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reseta contador de realizações para zero"""
    
    success = resetar_ciclo_habito(db, habito_id, current_user["sub"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito não encontrado"
        )
    
    # Buscar hábito atualizado
    habito = db.query(Habito).filter(Habito.id == habito_id).first()
    
    return DataResponse(data={
        "id": habito.id,
        "realizados_no_periodo": habito.realizados_no_periodo,
        "progresso": float(habito.progresso),
        "updated_at": habito.updated_at
    })

# Rota para listar hábitos por objetivo
@router.get("/objetivo/{objetivo_id}", response_model=DataResponse)
async def listar_habitos_por_objetivo(
    objetivo_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista hábitos de um objetivo específico"""
    
    query = db.query(Habito).filter(
        and_(
            Habito.objetivo_id == objetivo_id,
            Habito.usuario_id == current_user["sub"]
        )
    )
    
    total = query.count()
    offset = (page - 1) * limit
    habitos = query.offset(offset).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    pagination = PaginationResponse(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    habitos_data = serialize_models(habitos)
    return DataResponse(data=habitos_data, pagination=pagination)