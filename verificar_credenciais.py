#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir as credenciais do banco de dados.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.auth import get_password_hash, verify_password
from app.core.database import get_db
from app.models.usuario import Usuario
from datetime import datetime
import bcrypt

def verificar_credenciais():
    print("🔍 VERIFICANDO CREDENCIAIS NO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        
        # Buscar usuário no banco
        usuario_banco = db.query(Usuario).filter(Usuario.email == "teste@goalmanager.com").first()
        
        if usuario_banco:
            print("✅ Usuário encontrado no banco:")
            print(f"📧 Email: {usuario_banco.email}")
            print(f"🔑 Hash atual: {usuario_banco.senha_hash}")
            print(f"👤 Nome: {usuario_banco.nome}")
            print(f"🆔 ID: {usuario_banco.id}")
            print()
            
            # Hash que está no banco (fornecido pelo usuário)
            hash_banco = "$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi"
            
            print("🧪 TESTANDO DIFERENTES SENHAS COM O HASH DO BANCO:")
            print("-" * 50)
            
            senhas_teste = [
                "password",
                "secret", 
                "123456",
                "senha123",
                "senha123456",
                "teste123",
                "goalmanager",
                "admin"
            ]
            
            for senha in senhas_teste:
                try:
                    # Testar com bcrypt direto
                    resultado = bcrypt.checkpw(senha.encode('utf-8'), hash_banco.encode('utf-8'))
                    print(f"  🔑 '{senha}': {'✅ CORRETO!' if resultado else '❌ incorreto'}")
                    if resultado:
                        print(f"      🎉 SENHA ENCONTRADA: '{senha}'")
                        break
                except Exception as e:
                    print(f"  🔑 '{senha}': ❌ erro - {str(e)}")
            
            print()
            print("🔧 ATUALIZANDO CREDENCIAIS PARA NOSSOS TESTES:")
            print("-" * 50)
            
            # Atualizar para nossas credenciais de teste
            nova_senha = "senha123456"
            novo_hash = get_password_hash(nova_senha)
            
            # Atualizar usuário
            usuario_banco.email = "teste@exemplo.com"
            usuario_banco.senha_hash = novo_hash
            usuario_banco.nome = "Usuário de Teste"
            
            db.commit()
            db.refresh(usuario_banco)
            
            print(f"✅ Usuário atualizado:")
            print(f"📧 Email: {usuario_banco.email}")
            print(f"🔑 Nova senha: {nova_senha}")
            print(f"🔑 Novo hash: {novo_hash}")
            
            # Testar nova senha
            print()
            print("🧪 TESTANDO NOVA SENHA:")
            resultado = verify_password(nova_senha, novo_hash)
            print(f"✅ Verificação: {'SUCESSO' if resultado else 'FALHA'}")
            
        else:
            print("❌ Usuário 'teste@goalmanager.com' não encontrado no banco")
            print("🔍 Buscando outros usuários...")
            
            usuarios = db.query(Usuario).all()
            if usuarios:
                print("👥 Usuários encontrados:")
                for u in usuarios:
                    print(f"  📧 {u.email} - 👤 {u.nome} - 🆔 {u.id}")
            else:
                print("❌ Nenhum usuário encontrado no banco")
        
        # Fechar sessão
        db.close()
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕒 Verificação executada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    verificar_credenciais()