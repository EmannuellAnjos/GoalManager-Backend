"""
Script de Migração: Remover objetivo_id de tarefas
Data: 2025-11-01
Descrição: Remove a coluna objetivo_id e torna habito_id obrigatório
"""
import sqlite3
import os
import sys
from datetime import datetime

def fazer_backup(db_path):
    """Cria backup do banco de dados"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    print(f"📦 Criando backup em: {backup_path}")
    
    # Conectar aos bancos
    conn_origem = sqlite3.connect(db_path)
    conn_backup = sqlite3.connect(backup_path)
    
    # Copiar banco
    conn_origem.backup(conn_backup)
    
    conn_origem.close()
    conn_backup.close()
    
    print(f"✅ Backup criado com sucesso!")
    return backup_path

def verificar_dados(conn):
    """Verifica o estado atual dos dados"""
    cursor = conn.cursor()
    
    print("\n📊 Analisando dados existentes...")
    
    # Contar tarefas
    cursor.execute("SELECT COUNT(*) FROM tarefas")
    total = cursor.fetchone()[0]
    print(f"   Total de tarefas: {total}")
    
    # Tarefas com objetivo
    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE objetivo_id IS NOT NULL")
    com_objetivo = cursor.fetchone()[0]
    print(f"   Tarefas com objetivo_id: {com_objetivo}")
    
    # Tarefas com hábito
    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE habito_id IS NOT NULL")
    com_habito = cursor.fetchone()[0]
    print(f"   Tarefas com habito_id: {com_habito}")
    
    # Tarefas sem hábito (PROBLEMA!)
    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL")
    sem_habito = cursor.fetchone()[0]
    
    if sem_habito > 0:
        print(f"   ⚠️  ATENÇÃO: {sem_habito} tarefas SEM habito_id!")
        return False
    
    print(f"   ✅ Todas as tarefas têm habito_id")
    return True

def migrar_tabela(conn):
    """Executa a migração da tabela"""
    cursor = conn.cursor()
    
    print("\n🔄 Iniciando migração...")
    
    # 1. Criar nova tabela sem objetivo_id
    print("   1. Criando nova estrutura de tabela...")
    cursor.execute("""
        CREATE TABLE tarefas_new (
            id VARCHAR(36) PRIMARY KEY,
            usuario_id VARCHAR(36) NOT NULL,
            habito_id VARCHAR(36) NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            descricao TEXT,
            prioridade VARCHAR(10),
            status VARCHAR(20) NOT NULL DEFAULT 'backlog',
            estimativa_horas DECIMAL(6, 2),
            horas_gastas DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
            prazo DATE,
            progresso DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
            posicao INTEGER,
            tags TEXT,
            anexos TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Copiar dados
    print("   2. Copiando dados...")
    cursor.execute("""
        INSERT INTO tarefas_new (
            id, usuario_id, habito_id, titulo, descricao, prioridade,
            status, estimativa_horas, horas_gastas, prazo, progresso,
            posicao, tags, anexos, created_at, updated_at
        )
        SELECT 
            id, usuario_id, habito_id, titulo, descricao, prioridade,
            status, estimativa_horas, horas_gastas, prazo, progresso,
            posicao, tags, anexos, created_at, updated_at
        FROM tarefas
        WHERE habito_id IS NOT NULL
    """)
    
    registros_copiados = cursor.rowcount
    print(f"   ✅ {registros_copiados} registros copiados")
    
    # 3. Remover tabela antiga
    print("   3. Removendo tabela antiga...")
    cursor.execute("DROP TABLE tarefas")
    
    # 4. Renomear tabela nova
    print("   4. Renomeando tabela nova...")
    cursor.execute("ALTER TABLE tarefas_new RENAME TO tarefas")
    
    # 5. Recriar índices
    print("   5. Recriando índices...")
    indices = [
        "CREATE INDEX idx_tarefas_usuario_id ON tarefas(usuario_id)",
        "CREATE INDEX idx_tarefas_habito_id ON tarefas(habito_id)",
        "CREATE INDEX idx_tarefas_prioridade ON tarefas(prioridade)",
        "CREATE INDEX idx_tarefas_status ON tarefas(status)",
        "CREATE INDEX idx_tarefas_prazo ON tarefas(prazo)",
        "CREATE INDEX idx_tarefas_progresso ON tarefas(progresso)",
        "CREATE INDEX idx_tarefas_posicao ON tarefas(posicao)",
        "CREATE INDEX idx_tarefas_created_at ON tarefas(created_at)"
    ]
    
    for idx_sql in indices:
        cursor.execute(idx_sql)
    
    print(f"   ✅ {len(indices)} índices criados")
    
    # Commit
    conn.commit()
    print("\n✅ Migração concluída com sucesso!")

def verificar_resultado(conn):
    """Verifica o resultado da migração"""
    cursor = conn.cursor()
    
    print("\n🔍 Verificando resultado...")
    
    # Verificar estrutura
    cursor.execute("PRAGMA table_info(tarefas)")
    colunas = [row[1] for row in cursor.fetchall()]
    
    print(f"   Colunas na tabela: {', '.join(colunas)}")
    
    if 'objetivo_id' in colunas:
        print("   ❌ ERRO: objetivo_id ainda existe!")
        return False
    
    if 'habito_id' not in colunas:
        print("   ❌ ERRO: habito_id não existe!")
        return False
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM tarefas")
    total = cursor.fetchone()[0]
    print(f"   Total de tarefas após migração: {total}")
    
    # Verificar se todos têm habito_id
    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL")
    sem_habito = cursor.fetchone()[0]
    
    if sem_habito > 0:
        print(f"   ❌ ERRO: {sem_habito} tarefas sem habito_id!")
        return False
    
    print("   ✅ Estrutura correta!")
    print("   ✅ Todos os registros têm habito_id!")
    
    return True

def main():
    # Caminho do banco de dados
    db_path = "goalmanager.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Erro: Banco de dados não encontrado: {db_path}")
        print(f"   Verifique se você está no diretório correto")
        sys.exit(1)
    
    print("=" * 60)
    print("MIGRAÇÃO: Remover objetivo_id de tarefas")
    print("=" * 60)
    
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    
    try:
        # 1. Verificar dados
        if not verificar_dados(conn):
            print("\n⚠️  ATENÇÃO: Existem tarefas sem habito_id!")
            print("   Você precisa corrigir isso antes da migração.")
            print("\n   Opções:")
            print("   1. Deletar tarefas sem habito_id")
            print("   2. Atribuir um habito_id válido")
            print("   3. Cancelar a migração")
            
            resposta = input("\n   Digite 1, 2 ou 3: ").strip()
            
            if resposta == "1":
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tarefas WHERE habito_id IS NULL")
                conn.commit()
                print(f"   ✅ Tarefas sem habito_id foram removidas")
            elif resposta == "2":
                print("   Execute um UPDATE manualmente e rode o script novamente")
                sys.exit(0)
            else:
                print("   Migração cancelada")
                sys.exit(0)
        
        # 2. Fazer backup
        backup_path = fazer_backup(db_path)
        
        # 3. Confirmar
        print("\n⚠️  A migração irá:")
        print("   • Remover a coluna objetivo_id")
        print("   • Tornar habito_id obrigatório (NOT NULL)")
        print("   • Recriar todos os índices")
        print(f"\n   Backup criado em: {backup_path}")
        
        resposta = input("\n   Deseja continuar? (s/n): ").strip().lower()
        
        if resposta != 's':
            print("   Migração cancelada")
            sys.exit(0)
        
        # 4. Executar migração
        migrar_tabela(conn)
        
        # 5. Verificar resultado
        if verificar_resultado(conn):
            print("\n🎉 SUCESSO! Migração concluída!")
            print(f"   Backup mantido em: {backup_path}")
        else:
            print("\n❌ Erro na verificação!")
            print(f"   Você pode restaurar o backup: {backup_path}")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        print(f"   Você pode restaurar o backup que foi criado")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print("Próximos passos:")
    print("1. Reinicie o servidor backend")
    print("2. Teste a criação e edição de tarefas")
    print("3. Se tudo funcionar, você pode deletar o backup")
    print("=" * 60)

if __name__ == "__main__":
    main()

