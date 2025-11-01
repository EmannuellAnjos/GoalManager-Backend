"""
Script para limpar dados problemáticos e testar login
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models import Usuario
from app.services.auth import get_password_hash
from sqlalchemy.orm import Session

def clean_and_test():
    print("🧹 LIMPANDO DADOS PROBLEMÁTICOS E TESTANDO LOGIN")
    print("="*60)
    
    try:
        # Obter sessão do banco
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # 1. Limpar usuário de teste se existir
            print("1️⃣ Removendo usuário de teste antigo...")
            existing_user = db.query(Usuario).filter(Usuario.email == "teste@exemplo.com").first()
            if existing_user:
                db.delete(existing_user)
                db.commit()
                print("   ✅ Usuário antigo removido")
            else:
                print("   ℹ️ Nenhum usuário antigo encontrado")
            
            # 2. Criar novo usuário de teste
            print("\n2️⃣ Criando novo usuário de teste...")
            senha_teste = "senha123456"
            senha_hash = get_password_hash(senha_teste)
            
            novo_usuario = Usuario(
                nome="Usuário de Teste",
                email="teste@exemplo.com",
                senha_hash=senha_hash,
                ativo=True,
                email_verificado=True
            )
            
            db.add(novo_usuario)
            db.commit()
            db.refresh(novo_usuario)
            print(f"   ✅ Usuário criado com ID: {novo_usuario.id}")
            
            # 3. Testar verificação de senha
            print("\n3️⃣ Testando verificação de senha...")
            from app.services.auth import verify_password
            
            # Buscar usuário recém-criado
            usuario_teste = db.query(Usuario).filter(Usuario.email == "teste@exemplo.com").first()
            
            if usuario_teste:
                # Testar senha correta
                verificacao_correta = verify_password("senha123456", usuario_teste.senha_hash)
                print(f"   ✅ Senha correta: {verificacao_correta}")
                
                # Testar senha incorreta
                verificacao_incorreta = verify_password("senha_errada", usuario_teste.senha_hash)
                print(f"   ✅ Senha incorreta: {verificacao_incorreta}")
                
                if verificacao_correta and not verificacao_incorreta:
                    print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
                    print("\n📋 DADOS PARA TESTE:")
                    print("Email: teste@exemplo.com")
                    print("Senha: senha123456")
                    print("\n🚀 Agora você pode testar o login:")
                    print("1. Inicie o servidor: python run.py")
                    print("2. POST /api/v1/auth/login com os dados acima")
                    print("3. Ou execute: python test_login_fix.py")
                else:
                    print("\n❌ Problema na verificação de senhas")
            else:
                print("   ❌ Não foi possível encontrar o usuário criado")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_and_test()