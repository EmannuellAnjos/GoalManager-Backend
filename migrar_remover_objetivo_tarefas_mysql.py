"""
Script de Migração: Remover objetivo_id de tarefas (MySQL)
Data: 2025-11-01
Descrição: Remove a coluna objetivo_id e torna habito_id obrigatório no MySQL
"""
import pymysql
import sys
from datetime import datetime
from app.core.config import settings

def fazer_backup_sugestao():
    """Sugere fazer backup manualmente"""
    print("\n⚠️  IMPORTANTE: Faça backup do banco MySQL antes de continuar!")
    print("   Exemplo de backup:")
    print(f"   mysqldump -u {settings.mysql_user} -p {settings.mysql_database} > backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
    print()

def verificar_dados(conn):
    """Verifica o estado atual dos dados"""
    cursor = conn.cursor()
    
    print("\n📊 Analisando dados existentes...")
    
    try:
        # Contar tarefas
        cursor.execute("SELECT COUNT(*) as total FROM tarefas")
        result = cursor.fetchone()
        total = result['total'] if isinstance(result, dict) else result[0]
        print(f"   Total de tarefas: {total}")
        
        # Verificar se objetivo_id existe
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'tarefas'
            AND COLUMN_NAME = 'objetivo_id'
        """)
        result = cursor.fetchone()
        count = result['count'] if isinstance(result, dict) else result[0]
        objetivo_id_exists = count > 0
        print(f"   Coluna objetivo_id existe: {objetivo_id_exists}")
        
        if objetivo_id_exists:
            # Tarefas com objetivo
            cursor.execute("SELECT COUNT(*) as count FROM tarefas WHERE objetivo_id IS NOT NULL")
            result = cursor.fetchone()
            com_objetivo = result['count'] if isinstance(result, dict) else result[0]
            print(f"   Tarefas com objetivo_id: {com_objetivo}")
        
        # Tarefas com hábito
        cursor.execute("SELECT COUNT(*) as count FROM tarefas WHERE habito_id IS NOT NULL")
        result = cursor.fetchone()
        com_habito = result['count'] if isinstance(result, dict) else result[0]
        print(f"   Tarefas com habito_id: {com_habito}")
        
        # Tarefas sem hábito (PROBLEMA!)
        cursor.execute("SELECT COUNT(*) as count FROM tarefas WHERE habito_id IS NULL")
        result = cursor.fetchone()
        sem_habito = result['count'] if isinstance(result, dict) else result[0]
        
        if sem_habito > 0:
            print(f"   ⚠️  ATENÇÃO: {sem_habito} tarefas SEM habito_id!")
            return False, objetivo_id_exists
        
        print(f"   ✅ Todas as tarefas têm habito_id")
        return True, objetivo_id_exists
    except Exception as e:
        print(f"   ❌ Erro ao verificar dados: {e}")
        raise

def remover_indices_e_constraints(conn):
    """Remove índices e constraints relacionados a objetivo_id"""
    cursor = conn.cursor()
    
    print("\n🔍 Verificando índices e constraints...")
    
    # Verificar e remover foreign keys
    cursor.execute("""
        SELECT CONSTRAINT_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'tarefas'
        AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        AND CONSTRAINT_NAME LIKE '%objetivo%'
    """)
    
    fks = cursor.fetchall()
    for fk in fks:
        fk_name = fk['CONSTRAINT_NAME'] if isinstance(fk, dict) else fk[0]
        print(f"   Removendo foreign key: {fk_name}")
        cursor.execute(f"ALTER TABLE tarefas DROP FOREIGN KEY `{fk_name}`")
        conn.commit()
    
    # Verificar e remover índices
    cursor.execute("""
        SELECT INDEX_NAME
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'tarefas'
        AND COLUMN_NAME = 'objetivo_id'
    """)
    
    indices = cursor.fetchall()
    for idx in indices:
        idx_name = idx['INDEX_NAME'] if isinstance(idx, dict) else idx[0]
        if idx_name and idx_name != 'PRIMARY':  # Não remover primary key
            print(f"   Removendo índice: {idx_name}")
            cursor.execute(f"DROP INDEX `{idx_name}` ON tarefas")
            conn.commit()
    
    print("   ✅ Índices e constraints removidos")

def migrar_tabela(conn):
    """Executa a migração da tabela"""
    cursor = conn.cursor()
    
    print("\n🔄 Iniciando migração...")
    
    # 1. Remover índices e constraints primeiro
    remover_indices_e_constraints(conn)
    
    # 2. Verificar e corrigir tarefas sem habito_id
    cursor.execute("SELECT COUNT(*) as count FROM tarefas WHERE habito_id IS NULL")
    result = cursor.fetchone()
    sem_habito = result['count'] if isinstance(result, dict) else result[0]
    
    if sem_habito > 0:
        print(f"\n   ⚠️  Encontradas {sem_habito} tarefas sem habito_id")
        print("   Você precisa:")
        print("   1. Deletar essas tarefas: DELETE FROM tarefas WHERE habito_id IS NULL;")
        print("   2. OU atribuir um habito_id válido antes de continuar")
        
        resposta = input("\n   Deseja deletar tarefas sem habito_id? (s/n): ").strip().lower()
        if resposta == 's':
            cursor.execute("DELETE FROM tarefas WHERE habito_id IS NULL")
            conn.commit()
            print(f"   ✅ {cursor.rowcount} tarefas sem habito_id foram removidas")
        else:
            print("   Migração cancelada")
            sys.exit(0)
    
    # 3. Verificar se objetivo_id existe antes de tentar remover
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'tarefas'
        AND COLUMN_NAME = 'objetivo_id'
    """)
    
    result = cursor.fetchone()
    count = result['count'] if isinstance(result, dict) else result[0]
    objetivo_id_exists = count > 0
    
    if objetivo_id_exists:
        print("   3. Removendo coluna objetivo_id...")
        try:
            cursor.execute("ALTER TABLE tarefas DROP COLUMN objetivo_id")
            conn.commit()
            print("   ✅ Coluna objetivo_id removida")
        except Exception as e:
            print(f"   ❌ Erro ao remover coluna: {e}")
            print("   Verifique se há constraints ou índices ainda referenciando a coluna")
            raise
    else:
        print("   ⚠️  Coluna objetivo_id não existe (já foi removida?)")
    
    # 4. Garantir que habito_id é NOT NULL
    print("   4. Alterando habito_id para NOT NULL...")
    try:
        cursor.execute("ALTER TABLE tarefas MODIFY COLUMN habito_id VARCHAR(36) NOT NULL")
        conn.commit()
        print("   ✅ habito_id agora é NOT NULL")
    except Exception as e:
        print(f"   ⚠️  Aviso ao alterar habito_id: {e}")
    
    print("\n✅ Migração concluída com sucesso!")

def verificar_resultado(conn):
    """Verifica o resultado da migração"""
    cursor = conn.cursor()
    
    print("\n🔍 Verificando resultado...")
    
    # Verificar estrutura
    cursor.execute("DESCRIBE tarefas")
    rows = cursor.fetchall()
    colunas = [row['Field'] if isinstance(row, dict) else row[0] for row in rows]
    
    print(f"   Colunas na tabela: {', '.join(colunas)}")
    
    if 'objetivo_id' in colunas:
        print("   ❌ ERRO: objetivo_id ainda existe!")
        return False
    
    if 'habito_id' not in colunas:
        print("   ❌ ERRO: habito_id não existe!")
        return False
    
    # Verificar se é NOT NULL
    cursor.execute("""
        SELECT IS_NULLABLE 
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'tarefas'
        AND COLUMN_NAME = 'habito_id'
    """)
    result = cursor.fetchone()
    is_nullable = result['IS_NULLABLE'] if isinstance(result, dict) else result[0]
    
    if is_nullable == 'YES':
        print("   ⚠️  AVISO: habito_id ainda permite NULL")
    else:
        print("   ✅ habito_id é NOT NULL")
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) as count FROM tarefas")
    result = cursor.fetchone()
    total = result['count'] if isinstance(result, dict) else result[0]
    print(f"   Total de tarefas após migração: {total}")
    
    # Verificar se todos têm habito_id
    cursor.execute("SELECT COUNT(*) as count FROM tarefas WHERE habito_id IS NULL")
    result = cursor.fetchone()
    sem_habito = result['count'] if isinstance(result, dict) else result[0]
    
    if sem_habito > 0:
        print(f"   ❌ ERRO: {sem_habito} tarefas sem habito_id!")
        return False
    
    print("   ✅ Estrutura correta!")
    print("   ✅ Todos os registros têm habito_id!")
    
    return True

def main():
    fazer_backup_sugestao()
    
    # Confirmar antes de continuar
    resposta = input("   Você fez backup do banco? (s/n): ").strip().lower()
    if resposta != 's':
        print("   Por favor, faça o backup primeiro!")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("MIGRAÇÃO: Remover objetivo_id de tarefas (MySQL)")
    print("=" * 60)
    
    # Conectar ao banco
    try:
        conn = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"\n✅ Conectado ao MySQL: {settings.mysql_database}")
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao MySQL: {e}")
        print(f"   Verifique as credenciais em app/core/config.py")
        sys.exit(1)
    
    try:
        # 1. Verificar dados
        dados_ok, objetivo_id_exists = verificar_dados(conn)
        
        if not dados_ok:
            print("\n⚠️  Você precisa corrigir as tarefas sem habito_id antes da migração.")
            conn.close()
            sys.exit(1)
        
        if not objetivo_id_exists:
            print("\n⚠️  A coluna objetivo_id não existe no banco.")
            print("   A migração pode já ter sido executada ou a coluna nunca existiu.")
            if verificar_resultado(conn):
                print("\n✅ Tudo parece estar correto!")
            conn.close()
            sys.exit(0)
        
        # 2. Confirmar
        print("\n⚠️  A migração irá:")
        print("   • Remover a coluna objetivo_id")
        print("   • Tornar habito_id obrigatório (NOT NULL)")
        print("   • Remover índices e constraints relacionados")
        
        resposta = input("\n   Deseja continuar? (s/n): ").strip().lower()
        
        if resposta != 's':
            print("   Migração cancelada")
            conn.close()
            sys.exit(0)
        
        # 3. Executar migração
        migrar_tabela(conn)
        
        # 4. Verificar resultado
        if verificar_resultado(conn):
            print("\n🎉 SUCESSO! Migração concluída!")
        else:
            print("\n❌ Erro na verificação!")
            print("   Verifique manualmente o estado do banco")
            conn.rollback()
            sys.exit(1)
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERRO durante migração: {e}")
        print(f"\n📋 Detalhes do erro:")
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print("Próximos passos:")
    print("1. Reinicie o servidor backend")
    print("2. Teste a criação e edição de tarefas")
    print("=" * 60)

if __name__ == "__main__":
    main()

