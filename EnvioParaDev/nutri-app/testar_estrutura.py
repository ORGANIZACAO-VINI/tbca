# Script simplificado para testar a estrutura de integração
# Usa apenas métodos de verificação sem realmente conectar-se aos serviços

def testar_estrutura():
    """Verifica se os arquivos e diretórios necessários existem"""
    import os
    from pathlib import Path
    
    # Diretório atual
    current_dir = Path().absolute()
    print(f"Diretório atual: {current_dir}")
    
    # Verificar estrutura
    estrutura_ok = True
    
    # Verificar script de integração
    integracao_script = Path("iniciar-integracao.ps1")
    if integracao_script.exists():
        print("[OK] Script de integração encontrado")
    else:
        print("[ERRO] Script de integração não encontrado")
        estrutura_ok = False
    
    # Verificar pasta de backend
    backend_dir = Path("backend")
    if backend_dir.exists() and backend_dir.is_dir():
        print("[OK] Diretório backend encontrado")
        
        # Verificar requirements.txt
        if (backend_dir / "requirements.txt").exists():
            print("[OK] Arquivo requirements.txt encontrado")
        else:
            print("[ERRO] Arquivo requirements.txt não encontrado")
            estrutura_ok = False
    else:
        print("[ERRO] Diretório backend não encontrado")
        estrutura_ok = False
    
    # Verificar pasta de frontend
    frontend_dir = Path("frontend")
    if frontend_dir.exists() and frontend_dir.is_dir():
        print("[OK] Diretório frontend encontrado")
    else:
        print("[ERRO] Diretório frontend não encontrado")
        estrutura_ok = False
    
    # Verificar pasta de logs
    logs_dir = Path("logs")
    if not logs_dir.exists():
        try:
            os.makedirs(logs_dir)
            print("[OK] Diretório logs criado")
        except Exception as e:
            print(f"[ERRO] Não foi possível criar o diretório logs: {str(e)}")
            estrutura_ok = False
    else:
        print("[OK] Diretório logs encontrado")
    
    # Verificar documentação
    docs_dir = Path("docs")
    if docs_dir.exists() and docs_dir.is_dir():
        print("[OK] Diretório docs encontrado")
        
        # Verificar arquivo de integração
        integracao_doc = docs_dir / "INTEGRACAO_FRONTEND_BACKEND.md"
        if integracao_doc.exists():
            print("[OK] Documentação de integração encontrada")
        else:
            print("[AVISO] Documentação de integração não encontrada")
    else:
        print("[AVISO] Diretório docs não encontrado")
    
    # Verificar guia rápido
    guia_rapido = Path("GUIA_RAPIDO_INTEGRACAO.md")
    if guia_rapido.exists():
        print("[OK] Guia rápido de integração encontrado")
    else:
        print("[AVISO] Guia rápido de integração não encontrado")
    
    # Resultado final
    print("\n=== Resultado da Verificação ===")
    if estrutura_ok:
        print("[OK] Estrutura básica para integração está completa!")
    else:
        print("[AVISO] Há problemas na estrutura para integração.")
        print("Verifique os erros acima e corrija-os antes de continuar.")
    
    return estrutura_ok

if __name__ == "__main__":
    print("=== Verificando Estrutura de Integração ===\n")
    testar_estrutura()
