"""
Middleware personalizado para a aplicação
"""
from .logging import RequestLoggingMiddleware

__all__ = ["RequestLoggingMiddleware"]