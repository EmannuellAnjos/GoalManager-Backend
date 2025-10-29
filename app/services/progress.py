"""
Serviço para recálculo de progresso
Implementa as stored procedures em Python
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Objetivo, Habito, Tarefa
from decimal import Decimal
from typing import Optional

def recalcular_progresso_habito(db: Session, habito_id: str) -> Optional[Decimal]:
    """
    Recalcula o progresso de um hábito baseado nas realizações
    """
    try:
        # Buscar dados do hábito
        habito = db.query(Habito).filter(Habito.id == habito_id).first()
        if not habito:
            return None
        
        # Calcular novo progresso
        if habito.alvo_por_periodo > 0:
            novo_progresso = min(100.0, (habito.realizados_no_periodo / habito.alvo_por_periodo) * 100)
        else:
            novo_progresso = 0.0
        
        # Atualizar progresso
        habito.progresso = Decimal(str(novo_progresso))
        db.commit()
        
        # Recalcular progresso do objetivo pai
        if habito.objetivo_id:
            recalcular_progresso_objetivo(db, habito.objetivo_id)
        
        return habito.progresso
        
    except Exception as e:
        db.rollback()
        raise e

def recalcular_progresso_objetivo(db: Session, objetivo_id: str) -> Optional[Decimal]:
    """
    Recalcula o progresso de um objetivo baseado em hábitos e tarefas
    """
    try:
        # Buscar objetivo
        objetivo = db.query(Objetivo).filter(Objetivo.id == objetivo_id).first()
        if not objetivo:
            return None
        
        # Buscar progressos de hábitos
        habitos = db.query(Habito).filter(Habito.objetivo_id == objetivo_id).all()
        progresso_habitos = [h.progresso for h in habitos]
        
        # Buscar progressos de tarefas diretas (sem hábito)
        tarefas_diretas = db.query(Tarefa).filter(
            Tarefa.objetivo_id == objetivo_id,
            Tarefa.habito_id.is_(None)
        ).all()
        
        progresso_tarefas = []
        for t in tarefas_diretas:
            if t.status == 'concluida':
                progresso_tarefas.append(Decimal('100.00'))
            else:
                progresso_tarefas.append(t.progresso)
        
        # Calcular média dos progressos
        todos_progressos = progresso_habitos + progresso_tarefas
        
        if todos_progressos:
            novo_progresso = sum(todos_progressos) / len(todos_progressos)
        else:
            novo_progresso = Decimal('0.00')
        
        # Atualizar progresso do objetivo
        objetivo.progresso = novo_progresso
        db.commit()
        
        return objetivo.progresso
        
    except Exception as e:
        db.rollback()
        raise e

def marcar_habito_feito(
    db: Session, 
    habito_id: str, 
    usuario_id: str, 
    data_realizacao: str = None, 
    quantidade: int = 1
) -> bool:
    """
    Marca um hábito como feito incrementando o contador
    """
    try:
        # Buscar hábito
        habito = db.query(Habito).filter(
            Habito.id == habito_id,
            Habito.usuario_id == usuario_id
        ).first()
        
        if not habito:
            return False
        
        # Incrementar contador
        habito.realizados_no_periodo += quantidade
        db.commit()
        
        # Recalcular progresso
        recalcular_progresso_habito(db, habito_id)
        
        return True
        
    except Exception as e:
        db.rollback()
        raise e

def resetar_ciclo_habito(db: Session, habito_id: str, usuario_id: str) -> bool:
    """
    Reseta o contador de realizações de um hábito
    """
    try:
        # Buscar hábito
        habito = db.query(Habito).filter(
            Habito.id == habito_id,
            Habito.usuario_id == usuario_id
        ).first()
        
        if not habito:
            return False
        
        # Resetar contador
        habito.realizados_no_periodo = 0
        habito.progresso = Decimal('0.00')
        db.commit()
        
        # Recalcular progresso do objetivo pai
        if habito.objetivo_id:
            recalcular_progresso_objetivo(db, habito.objetivo_id)
        
        return True
        
    except Exception as e:
        db.rollback()
        raise e

def recalcular_todos_progressos(db: Session, usuario_id: str) -> bool:
    """
    Recalcula todos os progressos de um usuário
    """
    try:
        # Recalcular todos os hábitos
        habitos = db.query(Habito).filter(Habito.usuario_id == usuario_id).all()
        for habito in habitos:
            recalcular_progresso_habito(db, habito.id)
        
        # Recalcular todos os objetivos
        objetivos = db.query(Objetivo).filter(Objetivo.usuario_id == usuario_id).all()
        for objetivo in objetivos:
            recalcular_progresso_objetivo(db, objetivo.id)
        
        return True
        
    except Exception as e:
        db.rollback()
        raise e