"""
Script para corrigir trigger da tabela tarefas removendo referência a objetivo_id
"""
import pymysql
from app.core.config import settings
import sys

def get_db_connection():
    """Cria conexão direta com MySQL"""
    return pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        charset='utf8mb4'
    )

def encontrar_triggers(conn):
    """Encontra todos os triggers da tabela tarefas"""
    cursor = conn.cursor()
    
    query = """
    SELECT 
        TRIGGER_NAME,
        EVENT_MANIPULATION,
        ACTION_TIMING,
        ACTION_STATEMENT
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE TRIGGER_SCHEMA = DATABASE()
    AND EVENT_OBJECT_TABLE = 'tarefas'
    """
    
    cursor.execute(query)
    triggers = cursor.fetchall()
    cursor.close()
    
    return triggers

def remover_trigger(conn, trigger_name):
    """Remove um trigger específico"""
    cursor = conn.cursor()
    try:
        print(f"  [-] Removendo trigger: {trigger_name}")
        cursor.execute(f"DROP TRIGGER IF EXISTS `{trigger_name}`")
        conn.commit()
        print(f"  [OK] Trigger {trigger_name} removido com sucesso")
        return True
    except Exception as e:
        conn.rollback()
        print(f"  [ERRO] Erro ao remover trigger {trigger_name}: {e}")
        return False
    finally:
        cursor.close()

def criar_trigger_corrigido(conn):
    """Cria o trigger corrigido sem referência a objetivo_id"""
    cursor = conn.cursor()
    
    # Verificar se já existe
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
        AND TRIGGER_NAME = 'trg_tarefas_after_update'
    """)
    
    if cursor.fetchone()[0] > 0:
        print("  [!] Trigger trg_tarefas_after_update ja existe. Removendo...")
        cursor.execute("DROP TRIGGER IF EXISTS `trg_tarefas_after_update`")
        conn.commit()
    
    # Criar trigger corrigido
    trigger_sql = """
    CREATE TRIGGER trg_tarefas_after_update
    AFTER UPDATE ON tarefas
    FOR EACH ROW
    BEGIN
        -- Se status mudou para concluida, definir progresso como 100
        IF NEW.status = 'concluida' AND OLD.status != 'concluida' THEN
            UPDATE tarefas SET progresso = 100.00 WHERE id = NEW.id;
        END IF;
        
        -- NOTA: Recalcular progresso do habito e feito no codigo Python
        -- Nao precisa chamar stored procedure aqui, pois pode nao existir
        -- IF NEW.habito_id IS NOT NULL THEN
        --     CALL sp_recalcular_progresso_habito(NEW.habito_id);
        -- END IF;
        
        -- REMOVIDO: Nao ha mais objetivo_id
        -- IF NEW.objetivo_id IS NOT NULL THEN
        --     CALL sp_recalcular_progresso_objetivo(NEW.objetivo_id);
        -- END IF;
    END
    """
    
    try:
        print("  [*] Criando trigger corrigido...")
        cursor.execute(trigger_sql)
        conn.commit()
        print("  [OK] Trigger trg_tarefas_after_update criado com sucesso")
        return True
    except Exception as e:
        conn.rollback()
        print(f"  [ERRO] Erro ao criar trigger: {e}")
        return False
    finally:
        cursor.close()

def main():
    """Função principal"""
    print("=" * 70)
    print("CORRIGIR TRIGGER DA TABELA TAREFAS")
    print("Removendo referência a objetivo_id")
    print("=" * 70)
    
    conn = None
    try:
        # Conectar
        print("\n[*] Conectando ao MySQL...")
        conn = get_db_connection()
        print(f"[OK] Conectado: {settings.mysql_database}")
        
        # Encontrar triggers existentes
        print("\n[*] Buscando triggers na tabela tarefas...")
        triggers = encontrar_triggers(conn)
        
        triggers_para_remover = []
        
        if not triggers:
            print("  [i] Nenhum trigger encontrado na tabela tarefas")
        else:
            print(f"  [i] Encontrados {len(triggers)} trigger(s):")
            
            for trigger in triggers:
                trigger_name = trigger[0]
                action_statement = trigger[3] or ""
                print(f"\n  [>] Trigger: {trigger_name}")
                print(f"      Evento: {trigger[1]} | Timing: {trigger[2]}")
                
                # Verificar se menciona objetivo_id
                if 'objetivo_id' in action_statement.lower():
                    print(f"      [ATENCAO] Este trigger referencia 'objetivo_id'!")
                    triggers_para_remover.append(trigger_name)
        
        # Remover triggers que referenciam objetivo_id
        if triggers_para_remover:
            print(f"\n[-] Removendo {len(triggers_para_remover)} trigger(s) problematico(s)...")
            for trigger_name in triggers_para_remover:
                remover_trigger(conn, trigger_name)
        
        # Criar trigger corrigido
        print("\n[*] Criando trigger corrigido (sem objetivo_id)...")
        if criar_trigger_corrigido(conn):
            print("\n[OK] Trigger corrigido criado com sucesso!")
        else:
            print("\n[ERRO] Erro ao criar trigger corrigido")
            return False
        
        # Verificar resultado
        print("\n[*] Verificando triggers finais...")
        triggers_finais = encontrar_triggers(conn)
        print(f"  [i] Total de triggers: {len(triggers_finais)}")
        for trigger in triggers_finais:
            print(f"      - {trigger[0]} ({trigger[1]}, {trigger[2]})")
        
        print("\n" + "=" * 70)
        print("[OK] CORRECAO CONCLUIDA!")
        print("=" * 70)
        print("\n[i] NOTA: O recalculo de progresso dos habitos agora e feito")
        print("   no codigo Python (app/services/progress.py), nao mais no trigger.")
        print("   Isso permite mais controle e evita problemas com stored procedures.")
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()
            print("\n[*] Conexao fechada")

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)

