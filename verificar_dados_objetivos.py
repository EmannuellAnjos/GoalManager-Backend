#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar dados de objetivos no banco e identificar o problema.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.objetivo import Objetivo
from app.models.usuario import Usuario
from datetime import datetime

def verificar_dados_objetivos():
    print("🔍 VERIFICANDO DADOS DE OBJETIVOS NO BANCO")
    print("=" * 60)
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        
        # 1. Verificar usuários no banco
        print("👥 USUÁRIOS NO BANCO:")
        usuarios = db.query(Usuario).all()
        for usuario in usuarios:
            print(f"  🆔 {usuario.id}")
            print(f"  📧 {usuario.email}")
            print(f"  👤 {usuario.nome}")
            print(f"  ✅ Ativo: {usuario.ativo}")
            print()
        
        # 2. Verificar objetivos no banco
        print("🎯 OBJETIVOS NO BANCO:")
        objetivos = db.query(Objetivo).all()
        
        if objetivos:
            print(f"📊 Total de objetivos: {len(objetivos)}")
            for obj in objetivos:
                print(f"  🎯 ID: {obj.id}")
                print(f"  👤 Usuário ID: {obj.usuario_id}")
                print(f"  📝 Título: {obj.titulo}")
                print(f"  📅 Status: {obj.status}")
                print()
        else:
            print("❌ Nenhum objetivo encontrado no banco")
        
        # 3. Testar query específica com usuário demo
        print("🧪 TESTANDO QUERY COM USUÁRIO DEMO:")
        demo_user_id = "demo-user-123"
        objetivos_demo = db.query(Objetivo).filter(Objetivo.usuario_id == demo_user_id).all()
        print(f"  📊 Objetivos para '{demo_user_id}': {len(objetivos_demo)}")
        
        # 4. Testar query com usuário real
        print("🧪 TESTANDO QUERY COM USUÁRIO REAL:")
        if usuarios:
            user_real_id = usuarios[0].id
            objetivos_real = db.query(Objetivo).filter(Objetivo.usuario_id == user_real_id).all()
            print(f"  📊 Objetivos para '{user_real_id}': {len(objetivos_real)}")
            
            if objetivos_real:
                print("  ✅ OBJETIVOS ENCONTRADOS PARA USUÁRIO REAL!")
                for obj in objetivos_real:
                    print(f"    🎯 {obj.titulo} - Status: {obj.status}")
        
        # 5. Verificar configuração disable_auth
        from app.core.config import settings
        print(f"⚙️ CONFIGURAÇÃO disable_auth: {settings.disable_auth}")
        
        if settings.disable_auth:
            print("❗ PROBLEMA IDENTIFICADO:")
            print("  disable_auth=true está fazendo o sistema usar usuário demo")
            print("  mas os dados estão associados ao usuário real no banco!")
            print()
            print("💡 SOLUÇÕES:")
            print("  1. Alterar disable_auth=false no .env")
            print("  2. Ou criar dados de teste para o usuário demo")
        
        # Fechar sessão
        db.close()
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕒 Verificação executada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    verificar_dados_objetivos()