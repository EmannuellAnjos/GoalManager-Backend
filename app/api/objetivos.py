"""
Rotas da API - Objetivos
Implementa todas as operações CRUD para objetivos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional
from app.core.database import get_db
from app.models import Objetivo, Habito, Tarefa
from app.schemas import (
    ObjetivoCreate, ObjetivoUpdate, ObjetivoResponse, ObjetivoComEstatisticas,
    ObjetivoFilters, PaginationParams, PaginationResponse, DataResponse
)
from app.services.auth import get_current_user
from app.services.progress import recalcular_progresso_objetivo
from app.utils.serialization import serialize_model, serialize_models
from decimal import Decimal

router = APIRouter(prefix="/objetivos", tags=["objetivos"])

@router.get("", response_model=DataResponse)
async def listar_objetivos(
    busca: Optional[str] = Query(None, description="Busca em título e descrição"),
    status: Optional[List[str]] = Query(None, description="Filtro por status"),
    inicio: Optional[str] = Query(None, description="Data início mínima (YYYY-MM-DD)"),
    fim: Optional[str] = Query(None, description="Data fim máxima (YYYY-MM-DD)"), 
    order_by: str = Query("created_at", description="Campo para ordenação"),
    order_dir: str = Query("desc", pattern=r"^(asc|desc)$", description="Direção da ordenação"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista objetivos do usuário com filtros e paginação"""
    
    # Query base usando a view com estatísticas
    query = db.execute(text("""
        SELECT 
            o.*,
            COALESCE(COUNT(DISTINCT h.id), 0) as total_habitos,
            COALESCE(COUNT(DISTINCT CASE WHEN h.status = 'ativo' THEN h.id END), 0) as habitos_ativos,
            COALESCE(COUNT(DISTINCT t.id), 0) as total_tarefas,
            COALESCE(COUNT(DISTINCT CASE WHEN t.status = 'concluida' THEN t.id END), 0) as tarefas_concluidas,
            COALESCE(AVG(h.progresso), 0) as progresso_medio_habitos,
            COALESCE(AVG(CASE WHEN t.status = 'concluida' THEN 100 ELSE t.progresso END), 0) as progresso_medio_tarefas
        FROM objetivos o
        LEFT JOIN habitos h ON o.id = h.objetivo_id AND h.usuario_id = o.usuario_id
        LEFT JOIN tarefas t ON h.id = t.habito_id AND t.usuario_id = o.usuario_id
        WHERE o.usuario_id = :user_id
    """), {"user_id": current_user["sub"]})
    
    # Aplicar filtros
    conditions = ["o.usuario_id = :user_id"]
    params = {"user_id": current_user["sub"]}
    
    if busca:
        conditions.append("(o.titulo LIKE :busca OR o.descricao LIKE :busca)")
        params["busca"] = f"%{busca}%"
    
    if status:
        placeholders = ",".join([f":status_{i}" for i in range(len(status))])
        conditions.append(f"o.status IN ({placeholders})")
        for i, s in enumerate(status):
            params[f"status_{i}"] = s
    
    if inicio:
        conditions.append("o.inicio >= :inicio")
        params["inicio"] = inicio
        
    if fim:
        conditions.append("o.fim <= :fim")
        params["fim"] = fim
    
    # Query completa
    where_clause = " AND ".join(conditions)
    group_by = "GROUP BY o.id, o.usuario_id, o.titulo, o.descricao, o.inicio, o.fim, o.status, o.progresso, o.cor, o.icone, o.created_at, o.updated_at"
    order_clause = f"ORDER BY o.{order_by} {'DESC' if order_dir == 'desc' else 'ASC'}"
    
    # Query para total de registros
    count_query = f"""
        SELECT COUNT(DISTINCT o.id)
        FROM objetivos o
        WHERE {where_clause}
    """
    total = db.execute(text(count_query), params).scalar()
    
    # Query principal com paginação
    offset = (page - 1) * limit
    main_query = f"""
        SELECT 
            o.*,
            COALESCE(COUNT(DISTINCT h.id), 0) as total_habitos,
            COALESCE(COUNT(DISTINCT CASE WHEN h.status = 'ativo' THEN h.id END), 0) as habitos_ativos,
            COALESCE(COUNT(DISTINCT t.id), 0) as total_tarefas,
            COALESCE(COUNT(DISTINCT CASE WHEN t.status = 'concluida' THEN t.id END), 0) as tarefas_concluidas,
            COALESCE(AVG(h.progresso), 0) as progresso_medio_habitos,
            COALESCE(AVG(CASE WHEN t.status = 'concluida' THEN 100 ELSE t.progresso END), 0) as progresso_medio_tarefas
        FROM objetivos o
        LEFT JOIN habitos h ON o.id = h.objetivo_id AND h.usuario_id = o.usuario_id
        LEFT JOIN tarefas t ON h.id = t.habito_id AND t.usuario_id = o.usuario_id
        WHERE {where_clause}
        {group_by}
        {order_clause}
        LIMIT {limit} OFFSET {offset}
    """
    
    resultados = db.execute(text(main_query), params).fetchall()
    
    # Converter para formato de resposta
    objetivos = []
    for row in resultados:
        objetivo = {
            "id": row[0],
            "usuario_id": row[1], 
            "titulo": row[2],
            "descricao": row[3],
            "inicio": row[4],
            "fim": row[5],
            "status": row[6],
            "progresso": row[7],
            "cor": row[8],
            "icone": row[9],
            "created_at": row[10],
            "updated_at": row[11],
            "total_habitos": row[12],
            "habitos_ativos": row[13],
            "total_tarefas": row[14],
            "tarefas_concluidas": row[15],
            "progresso_medio_habitos": row[16],
            "progresso_medio_tarefas": row[17]
        }
        objetivos.append(objetivo)
    
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
    
    return DataResponse(data=objetivos, pagination=pagination)

@router.get("/{objetivo_id}", response_model=DataResponse)
async def obter_objetivo(
    objetivo_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém um objetivo específico"""
    
    objetivo = db.query(Objetivo).filter(
        and_(
            Objetivo.id == objetivo_id,
            Objetivo.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo não encontrado"
        )
    
    return DataResponse(data=serialize_model(objetivo))

@router.post("", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
async def criar_objetivo(
    objetivo_data: ObjetivoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria um novo objetivo"""
    
    # Criar novo objetivo
    novo_objetivo = Objetivo(
        usuario_id=current_user["sub"],
        **objetivo_data.model_dump()
    )
    
    db.add(novo_objetivo)
    db.commit()
    db.refresh(novo_objetivo)
    
    return DataResponse(data=serialize_model(novo_objetivo))

@router.put("/{objetivo_id}", response_model=DataResponse)
async def atualizar_objetivo(
    objetivo_id: str,
    objetivo_data: ObjetivoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza um objetivo existente"""
    
    objetivo = db.query(Objetivo).filter(
        and_(
            Objetivo.id == objetivo_id,
            Objetivo.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = objetivo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(objetivo, field, value)
    
    db.commit()
    db.refresh(objetivo)
    
    # Recalcular progresso se necessário
    recalcular_progresso_objetivo(db, objetivo_id)
    
    return DataResponse(data=serialize_model(objetivo))

@router.delete("/{objetivo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_objetivo(
    objetivo_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove um objetivo e todos os hábitos/tarefas vinculados"""
    
    objetivo = db.query(Objetivo).filter(
        and_(
            Objetivo.id == objetivo_id,
            Objetivo.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo não encontrado"
        )
    
    # Remover hábitos e tarefas vinculados
    db.query(Habito).filter(Habito.objetivo_id == objetivo_id).delete()
    db.query(Tarefa).filter(Tarefa.objetivo_id == objetivo_id).delete()
    
    # Remover objetivo
    db.delete(objetivo)
    db.commit()

@router.delete("", response_model=DataResponse)
async def deletar_objetivos_lote(
    ids: List[str],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove múltiplos objetivos"""
    
    # Verificar se todos os objetivos pertencem ao usuário
    objetivos = db.query(Objetivo).filter(
        and_(
            Objetivo.id.in_(ids),
            Objetivo.usuario_id == current_user["sub"]
        )
    ).all()
    
    if len(objetivos) != len(ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou mais objetivos não foram encontrados"
        )
    
    # Remover hábitos e tarefas vinculados
    for objetivo_id in ids:
        db.query(Habito).filter(Habito.objetivo_id == objetivo_id).delete()
        db.query(Tarefa).filter(Tarefa.objetivo_id == objetivo_id).delete()
    
    # Remover objetivos
    deleted_count = db.query(Objetivo).filter(
        and_(
            Objetivo.id.in_(ids),
            Objetivo.usuario_id == current_user["sub"]
        )
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return DataResponse(data={
        "message": f"{deleted_count} objetivos removidos com sucesso",
        "deleted_count": deleted_count
    })

@router.get("/{objetivo_id}/habitos", response_model=DataResponse)
async def listar_habitos_do_objetivo(
    objetivo_id: str,
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista hábitos de um objetivo específico"""
    
    # Verificar se o objetivo existe e pertence ao usuário
    objetivo = db.query(Objetivo).filter(
        and_(
            Objetivo.id == objetivo_id,
            Objetivo.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo não encontrado"
        )
    
    # Query para buscar hábitos do objetivo
    query = db.query(Habito).filter(
        and_(
            Habito.objetivo_id == objetivo_id,
            Habito.usuario_id == current_user["sub"]
        )
    )
    
    # Total de registros
    total = query.count()
    
    # Paginação
    offset = (page - 1) * limit
    habitos = query.order_by(desc(Habito.created_at)).offset(offset).limit(limit).all()
    
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

@router.get("/{objetivo_id}/tarefas", response_model=DataResponse)
async def listar_tarefas_do_objetivo(
    objetivo_id: str,
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista tarefas de um objetivo específico através dos hábitos do objetivo"""
    
    # Verificar se o objetivo existe e pertence ao usuário
    objetivo = db.query(Objetivo).filter(
        and_(
            Objetivo.id == objetivo_id,
            Objetivo.usuario_id == current_user["sub"]
        )
    ).first()
    
    if not objetivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objetivo não encontrado"
        )
    
    # Buscar IDs dos hábitos do objetivo
    habitos_ids = db.query(Habito.id).filter(
        and_(
            Habito.objetivo_id == objetivo_id,
            Habito.usuario_id == current_user["sub"]
        )
    ).subquery()
    
    # Query para buscar tarefas através dos hábitos do objetivo
    query = db.query(Tarefa).filter(
        and_(
            Tarefa.habito_id.in_(habitos_ids),
            Tarefa.usuario_id == current_user["sub"]
        )
    )
    
    # Total de registros
    total = query.count()
    
    # Paginação
    offset = (page - 1) * limit
    tarefas = query.order_by(desc(Tarefa.created_at)).offset(offset).limit(limit).all()
    
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
    
    tarefas_data = serialize_models(tarefas)
    return DataResponse(data=tarefas_data, pagination=pagination)