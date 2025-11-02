"""
Utilitários para serialização de objetos SQLAlchemy
"""
from typing import Any, Dict, List
from sqlalchemy.orm import class_mapper
from sqlalchemy.inspection import inspect
from datetime import datetime, date
from decimal import Decimal
from app.schemas.tarefa import TarefaResponse

def serialize_model(model_instance) -> Dict[str, Any]:
    """
    Serializa uma instância de modelo SQLAlchemy de forma segura.
    Remove o InstanceState e converte tipos especiais.
    """
    if model_instance is None:
        return None
        
    # Obter todas as colunas do modelo
    mapper = class_mapper(model_instance.__class__)
    columns = [column.key for column in mapper.columns]
    
    result = {}
    for column in columns:
        value = getattr(model_instance, column, None)
        
        # Converter tipos especiais para JSON serializável
        if isinstance(value, datetime):
            result[column] = value.isoformat()
        elif isinstance(value, date):
            result[column] = value.isoformat()
        elif isinstance(value, Decimal):
            result[column] = float(value)
        else:
            result[column] = value
            
    return result

def serialize_models(model_instances: List) -> List[Dict[str, Any]]:
    """
    Serializa uma lista de instâncias de modelo SQLAlchemy.
    """
    return [serialize_model(instance) for instance in model_instances]

def serialize_tarefa(tarefa_instance) -> Dict[str, Any]:
    """
    Serializa uma tarefa usando o schema Pydantic para garantir camelCase
    e incluir todos os campos (estimativa_horas, horas_gastas, etc).
    """
    if tarefa_instance is None:
        return None
    
    return TarefaResponse.model_validate(tarefa_instance).model_dump(
        by_alias=True,
        exclude_none=False  # Incluir campos None para garantir que todos os campos apareçam
    )

def serialize_tarefas(tarefa_instances: List) -> List[Dict[str, Any]]:
    """
    Serializa uma lista de tarefas usando o schema Pydantic.
    Garante camelCase e inclui todos os campos.
    """
    return [serialize_tarefa(tarefa) for tarefa in tarefa_instances]