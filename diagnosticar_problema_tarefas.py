"""
Script para diagnosticar o problema com objetivo_id em tarefas
"""
from sqlalchemy import inspect, text
from app.core.database import engine, Base
from app.models import Tarefa

print("=" * 60)
print("DIAGNOSTICO: Problema objetivo_id em Tarefas")
print("=" * 60)

# 1. Verificar estrutura do modelo Python
print("\n1. ESTRUTURA DO MODELO PYTHON:")
print("   Colunas definidas no modelo Tarefa:")
for column in Tarefa.__table__.columns:
    print(f"      - {column.name} ({column.type})")

if hasattr(Tarefa, 'objetivo_id'):
    print("\n   [ERRO] PROBLEMA: objetivo_id ainda existe no modelo Python!")
else:
    print("\n   [OK] objetivo_id NAO existe no modelo Python (correto)")

# 2. Verificar estrutura no banco de dados
print("\n2. ESTRUTURA NO BANCO DE DADOS:")
inspector = inspect(engine)

try:
    columns_db = [col['name'] for col in inspector.get_columns('tarefas')]
    print("   Colunas na tabela tarefas (do banco):")
    for col in columns_db:
        print(f"      - {col}")
    
    if 'objetivo_id' in columns_db:
        print("\n   ❌ PROBLEMA: objetivo_id ainda existe no banco!")
        print("      Execute: ALTER TABLE tarefas DROP COLUMN objetivo_id;")
    else:
        print("\n   ✅ objetivo_id NÃO existe no banco (correto)")
except Exception as e:
    print(f"   ⚠️  Erro ao verificar: {e}")

# 3. Verificar índices no banco
print("\n3️⃣ ÍNDICES NO BANCO DE DADOS:")
try:
    indexes = inspector.get_indexes('tarefas')
    print("   Índices encontrados:")
    for idx in indexes:
        cols = idx.get('column_names', [])
        print(f"      - {idx['name']}: {cols}")
        
        if 'objetivo_id' in cols:
            print(f"         [ERRO] PROBLEMA: Indice inclui objetivo_id!")
            print(f"         Remova com: DROP INDEX {idx['name']} ON tarefas;")
except Exception as e:
    print(f"   [AVISO] Erro ao verificar: {e}")

# 4. Verificar foreign keys
print("\n4. FOREIGN KEYS NO BANCO:")
try:
    fks = inspector.get_foreign_keys('tarefas')
    if fks:
        print("   Foreign keys encontradas:")
        for fk in fks:
            cols = fk.get('constrained_columns', [])
            print(f"      - {fk['name']}: {cols}")
            if 'objetivo_id' in cols:
                print(f"         [ERRO] PROBLEMA: FK inclui objetivo_id!")
                print(f"         Remova com: ALTER TABLE tarefas DROP FOREIGN KEY {fk['name']};")
    else:
        print("   [OK] Nenhuma foreign key encontrada")
except Exception as e:
    print(f"   [AVISO] Erro ao verificar: {e}")

# 5. Verificar SQL direto
print("\n5. VERIFICACAO SQL DIRETA:")
try:
    with engine.connect() as conn:
        # Verificar se objetivo_id existe
        result = conn.execute(text("""
            SELECT COUNT(*) as existe
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'tarefas'
            AND COLUMN_NAME = 'objetivo_id'
        """))
        existe = result.fetchone()[0]
        
        if existe > 0:
            print("   [ERRO] objetivo_id EXISTE no banco (via INFORMATION_SCHEMA)")
        else:
            print("   [OK] objetivo_id NAO existe no banco (via INFORMATION_SCHEMA)")
        
        # Tentar SELECT direto
        try:
            result = conn.execute(text("SELECT objetivo_id FROM tarefas LIMIT 1"))
            print("   [ERRO] Conseguiu fazer SELECT objetivo_id (coluna existe!)")
        except Exception as e:
            if "Unknown column" in str(e):
                print("   [OK] SELECT objetivo_id falhou (coluna nao existe - correto)")
            else:
                print(f"   [AVISO] Erro diferente: {e}")
except Exception as e:
    print(f"   [AVISO] Erro na verificacao SQL: {e}")

# 6. Verificar metadata do SQLAlchemy
print("\n6. METADATA DO SQLALCHEMY:")
print("   Colunas no metadata do SQLAlchemy:")
for col in Tarefa.__table__.columns:
    print(f"      - {col.name}")

if 'objetivo_id' in [col.name for col in Tarefa.__table__.columns]:
    print("\n   [ERRO] PROBLEMA: objetivo_id no metadata do SQLAlchemy!")
else:
    print("\n   [OK] objetivo_id NAO esta no metadata (correto)")

print("\n" + "=" * 60)
print("CONCLUSAO:")
print("=" * 60)
print("Se objetivo_id aparece em QUALQUER lugar acima, esse e o problema!")
print("Execute os comandos SQL sugeridos para remover.")
print("=" * 60)

