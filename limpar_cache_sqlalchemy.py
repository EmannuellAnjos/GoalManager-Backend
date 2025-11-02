"""
Script para limpar cache do SQLAlchemy e recarregar metadata
"""
from app.core.database import engine, Base
from sqlalchemy import inspect

print("🔄 Limpando cache do SQLAlchemy...")

# Forçar recarregamento do metadata
Base.metadata.clear()

# Recarregar todos os modelos
from app.models import Tarefa, Habito, Objetivo, Usuario, HabitoRealizacao, AuditLog

# Recriar todas as tabelas no metadata (sem alterar o banco)
Base.metadata.reflect(bind=engine)

# Verificar estrutura da tabela tarefas no banco
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('tarefas')]

print(f"\n📋 Colunas na tabela tarefas (do banco):")
for col in columns:
    print(f"   - {col}")

if 'objetivo_id' in columns:
    print("\n❌ PROBLEMA: objetivo_id ainda existe no banco de dados!")
    print("   Execute o script SQL para remover:")
    print("   ALTER TABLE tarefas DROP COLUMN objetivo_id;")
else:
    print("\n✅ objetivo_id não existe mais na tabela")

# Verificar índices
indexes = inspector.get_indexes('tarefas')
print(f"\n📋 Índices na tabela tarefas:")
for idx in indexes:
    print(f"   - {idx['name']}: {idx['column_names']}")
    
    # Verificar se algum índice inclui objetivo_id
    if 'objetivo_id' in idx.get('column_names', []):
        print(f"      ⚠️  PROBLEMA: Índice {idx['name']} inclui objetivo_id!")
        print(f"      Remova com: DROP INDEX {idx['name']} ON tarefas;")

# Verificar foreign keys
fks = inspector.get_foreign_keys('tarefas')
print(f"\n📋 Foreign Keys na tabela tarefas:")
for fk in fks:
    print(f"   - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

print("\n✅ Cache limpo! Reinicie o servidor para aplicar.")

