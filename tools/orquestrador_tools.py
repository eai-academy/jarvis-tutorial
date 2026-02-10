"""
Orquestrador de Tools para JARVIS v4/v5
Carrega e gerencia ferramentas de forma modular
Cada ferramenta está em seu próprio arquivo na pasta tools/
"""

import json
import sys
from typing import Any, Dict, List
from pathlib import Path

# Importa todas as ferramentas
from tools import (
    FerramentaHora,
    FerramentaClima,
    FerramentaBuscarWeb,
    FerramentaSistemaArquivos
)


class OrquestradorDeTools:
    """
    Orquestrador de Ferramentas para JARVIS
    
    Carrega ferramentas dinamicamente e gerencia comunicação via stdin/stdout
    
    Protocolo:
    - Cliente envia JSON: {"method": "call_tool", "params": {"name": "tool_name", "arguments": {...}}}
    - Servidor responde JSON: {"result": ..., "error": None} ou {"result": None, "error": "mensagem"}
    """
    
    def __init__(self):
        """Inicializa o servidor e registra todas as ferramentas"""
        self.ferramentas = {}
        self._registrar_ferramentas()
    
    def _registrar_ferramentas(self):
        """Registra todas as ferramentas disponíveis"""
        # Lista de classes de ferramentas
        classes_ferramentas = [
            FerramentaHora,
            FerramentaClima,
            FerramentaBuscarWeb,
        ]
        
        # Adiciona ferramentas de sistema de arquivos
        classes_ferramentas.extend(FerramentaSistemaArquivos.obter_todas())
        
        # Registra cada ferramenta
        for classe_ferramenta in classes_ferramentas:
            nome = classe_ferramenta.nome()
            self.ferramentas[nome] = classe_ferramenta
            
        print(f"✅ {len(self.ferramentas)} ferramentas registradas", file=sys.stderr)
    
    def chamar_ferramenta(self, nome: str, argumentos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chama uma ferramenta pelo nome com os argumentos fornecidos
        
        Args:
            nome: nome da ferramenta
            argumentos: dicionário com argumentos para a ferramenta
        
        Returns:
            Dicionário com result e error
        """
        if nome not in self.ferramentas:
            return {
                "result": None,
                "error": f"Ferramenta '{nome}' não encontrada. Disponíveis: {list(self.ferramentas.keys())}"
            }
        
        try:
            classe_ferramenta = self.ferramentas[nome]
            resultado = classe_ferramenta.executar(**argumentos)
            return {"result": resultado, "error": None}
        except TypeError as e:
            return {
                "result": None,
                "error": f"Argumentos inválidos para {nome}: {str(e)}"
            }
        except Exception as e:
            return {
                "result": None,
                "error": f"Erro ao executar {nome}: {str(e)}"
            }
    
    def obter_lista_ferramentas(self) -> List[Dict]:
        """
        Retorna lista de ferramentas disponíveis com descrições
        
        Returns:
            Lista de dicionários com informações de cada ferramenta
        """
        lista = []
        
        for nome, classe_ferramenta in self.ferramentas.items():
            info = {
                "name": nome,
                "description": classe_ferramenta.descricao(),
                "parameters": classe_ferramenta.parametros()
            }
            lista.append(info)
        
        return lista
    
    def processar_requisicao(self, requisicao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma requisição do orquestrador
        
        Args:
            requisicao: dicionário com method e params
        
        Returns:
            Resposta com result ou error
        """
        metodo = requisicao.get("method")
        parametros = requisicao.get("params", {})
        
        if metodo == "list_tools":
            return {"result": self.obter_lista_ferramentas(), "error": None}
        
        elif metodo == "call_tool":
            nome = parametros.get("name")
            argumentos = parametros.get("arguments", {})
            return self.chamar_ferramenta(nome, argumentos)
        
        else:
            return {"result": None, "error": f"Método '{metodo}' não reconhecido"}
    
    def executar(self):
        """
        Loop principal do servidor - lê stdin, processa, escreve stdout
        """
        # Envia mensagem de inicialização
        mensagem_init = {
            "status": "ready",
            "tools": list(self.ferramentas.keys())
        }
        print(json.dumps(mensagem_init, ensure_ascii=False), flush=True)
        
        # Loop de processamento
        for linha in sys.stdin:
            try:
                requisicao = json.loads(linha.strip())
                resposta = self.processar_requisicao(requisicao)
                print(json.dumps(resposta, ensure_ascii=False), flush=True)
            except json.JSONDecodeError as e:
                resposta_erro = {
                    "result": None,
                    "error": f"JSON inválido: {str(e)}"
                }
                print(json.dumps(resposta_erro, ensure_ascii=False), flush=True)
            except Exception as e:
                resposta_erro = {
                    "result": None,
                    "error": f"Erro interno: {str(e)}"
                }
                print(json.dumps(resposta_erro, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    orquestrador = OrquestradorDeTools()
    orquestrador.executar()
