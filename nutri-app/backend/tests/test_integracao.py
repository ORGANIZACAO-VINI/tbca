"""
Script para testar a conexão entre frontend e backend
"""

import requests
import json
import sys
from pathlib import Path

# URLs
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def testar_backend():
    """Testa os endpoints do backend"""
    print("\n=== Testando Backend ===")
    
    try:
        # Testar endpoint raiz
        response = requests.get(f"{BACKEND_URL}/")
        print(f"/ - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Resposta: {response.json()}")
        
        # Testar endpoint de grupos
        response = requests.get(f"{BACKEND_URL}/grupos")
        print(f"/grupos - Status: {response.status_code}")
        if response.status_code == 200:
            grupos = response.json()
            print(f"Grupos encontrados: {len(grupos)}")
            if grupos:
                print(f"Primeiro grupo: {grupos[0]['nome']}")
        
        # Testar endpoint de alimentos
        response = requests.get(f"{BACKEND_URL}/alimentos?limit=5")
        print(f"/alimentos - Status: {response.status_code}")
        if response.status_code == 200:
            alimentos = response.json()
            print(f"Alimentos encontrados: {len(alimentos)}")
            if alimentos:
                print(f"Primeiro alimento: {alimentos[0]['nome']}")
        
        # Testar busca de alimentos
        if alimentos:
            nome_parcial = alimentos[0]['nome'].split()[0]
            response = requests.get(f"{BACKEND_URL}/alimentos/search?q={nome_parcial}")
            print(f"/alimentos/search - Status: {response.status_code}")
            if response.status_code == 200:
                resultados = response.json()
                print(f"Resultados da busca por '{nome_parcial}': {len(resultados)}")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar ao backend. Verifique se o servidor está rodando.")
        return False
    
    except Exception as e:
        print(f"Erro ao testar backend: {str(e)}")
        return False

def testar_frontend():
    """Verifica se o frontend está acessível"""
    print("\n=== Testando Frontend ===")
    
    try:
        response = requests.get(FRONTEND_URL)
        print(f"Frontend - Status: {response.status_code}")
        if response.status_code == 200:
            print("Frontend está acessível")
        return True
    
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar ao frontend. Verifique se o servidor Next.js está rodando.")
        return False
    
    except Exception as e:
        print(f"Erro ao testar frontend: {str(e)}")
        return False

def verificar_integracao():
    """Verifica a integração entre frontend e backend"""
    backend_ok = testar_backend()
    frontend_ok = testar_frontend()
    
    print("\n=== Resultado do Teste ===")
    if backend_ok and frontend_ok:
        print("[OK] Backend e Frontend estao rodando e acessiveis.")
        print("Para testar a integracao completa, abra o frontend no navegador:")
        print(f"{FRONTEND_URL}")
    else:
        if not backend_ok:
            print("[ERRO] Backend nao esta funcionando corretamente.")
            print("Dica: Execute 'uvicorn app.main:app --reload' na pasta backend.")
        if not frontend_ok:
            print("[ERRO] Frontend nao esta funcionando corretamente.")
            print("Dica: Execute 'npm run dev' na pasta frontend.")

if __name__ == "__main__":
    verificar_integracao()
