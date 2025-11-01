"""
Utilitários para serialização de objetos SQLAlchemy
"""
from typing import Any, Dict, List
from sqlalchemy.orm import class_mapper
from sqlalchemy.inspection import inspect
from datetime import datetime, date
from decimal import Decimal

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