#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilitários para configuração e manutenção do ambiente Oracle
"""

import json
import os
import sys
from pathlib import Path

def create_oracle_config():
    """Cria um arquivo de configuração Oracle interativo"""
    print("=== Configuração Interativa do Oracle ===")
    
    config = {}
    
    # Informações básicas de conexão
    print("\n1. Informações de Conexão:")
    config['ORACLE_HOST'] = input("Host do Oracle (padrão: localhost): ").strip() or "localhost"
    config['ORACLE_PORT'] = input("Porta do Oracle (padrão: 1521): ").strip() or "1521"
    config['ORACLE_SERVICE'] = input("Service Name (padrão: XEPDB1): ").strip() or "XEPDB1"
    config['ORACLE_USER'] = input("Usuário do Oracle: ").strip()
    
    if not config['ORACLE_USER']:
        print("❌ Usuário é obrigatório!")
        return False
    
    config['ORACLE_PASSWORD'] = input("Senha do Oracle: ").strip()
    
    if not config['ORACLE_PASSWORD']:
        print("❌ Senha é obrigatória!")
        return False
    
    # Configurações avançadas
    print("\n2. Configurações Avançadas:")
    config['ORACLE_TABLESPACE'] = input("Tablespace (padrão: USERS): ").strip() or "USERS"
    config['ORACLE_TEMP_TABLESPACE'] = input("Temp Tablespace (padrão: TEMP): ").strip() or "TEMP"
    
    # Pool de conexões
    print("\n3. Pool de Conexões:")
    min_conn = input("Mínimo de conexões (padrão: 2): ").strip()
    max_conn = input("Máximo de conexões (padrão: 10): ").strip()
    increment = input("Incremento de conexões (padrão: 1): ").strip()
    
    config['CONNECTION_POOL'] = {
        "min_connections": int(min_conn) if min_conn else 2,
        "max_connections": int(max_conn) if max_conn else 10,
        "increment": int(increment) if increment else 1
    }
    
    # Performance
    iterations = input("Iterações padrão para testes (padrão: 5): ").strip()
    concurrency = input("Máxima concorrência para testes (padrão: 20): ").strip()
    
    config['PERFORMANCE'] = {
        "default_iterations": int(iterations) if iterations else 5,
        "max_concurrency": int(concurrency) if concurrency else 20
    }
    
    # Logging
    config['LOGGING'] = {
        "level": "INFO",
        "enable_performance_logs": True,
        "enable_detailed_errors": True
    }
    
    # Salvar configuração
    config_dir = Path(__file__).parent.parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "oracle_config.json"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Configuração salva em: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {str(e)}")
        return False

def validate_oracle_config(config_path=None):
    """Valida arquivo de configuração Oracle"""
    if not config_path:
        config_path = Path(__file__).parent.parent / "config" / "oracle_config.json"
    
    if not Path(config_path).exists():
        print(f"❌ Arquivo de configuração não encontrado: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ['ORACLE_USER', 'ORACLE_PASSWORD', 'ORACLE_HOST', 
                          'ORACLE_PORT', 'ORACLE_SERVICE']
        
        missing_fields = [field for field in required_fields if field not in config or not config[field]]
        
        if missing_fields:
            print(f"❌ Campos obrigatórios ausentes: {', '.join(missing_fields)}")
            return False
        
        print("✅ Configuração válida!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro ao validar configuração: {str(e)}")
        return False

def backup_oracle_config():
    """Cria backup da configuração atual"""
    config_file = Path(__file__).parent.parent / "config" / "oracle_config.json"
    
    if not config_file.exists():
        print("❌ Nenhuma configuração para fazer backup!")
        return False
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = config_file.parent / f"oracle_config_backup_{timestamp}.json"
    
    try:
        import shutil
        shutil.copy2(config_file, backup_file)
        print(f"✅ Backup criado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {str(e)}")
        return False

def list_oracle_configs():
    """Lista todas as configurações Oracle disponíveis"""
    config_dir = Path(__file__).parent.parent / "config"
    
    if not config_dir.exists():
        print("❌ Diretório de configuração não existe!")
        return
    
    configs = list(config_dir.glob("oracle_config*.json"))
    
    if not configs:
        print("❌ Nenhuma configuração Oracle encontrada!")
        return
    
    print("📁 Configurações Oracle encontradas:")
    for i, config_file in enumerate(configs, 1):
        size = config_file.stat().st_size
        modified = config_file.stat().st_mtime
        from datetime import datetime
        mod_time = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i}. {config_file.name} ({size} bytes, modificado: {mod_time})")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Utilitários de configuração Oracle')
    parser.add_argument('action', choices=['create', 'validate', 'backup', 'list'], 
                       help='Ação a executar')
    parser.add_argument('--config', help='Caminho para arquivo de configuração')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        success = create_oracle_config()
        sys.exit(0 if success else 1)
    elif args.action == 'validate':
        success = validate_oracle_config(args.config)
        sys.exit(0 if success else 1)
    elif args.action == 'backup':
        success = backup_oracle_config()
        sys.exit(0 if success else 1)
    elif args.action == 'list':
        list_oracle_configs()
        sys.exit(0)

if __name__ == "__main__":
    main()
