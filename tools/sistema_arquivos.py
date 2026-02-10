"""
Ferramenta: Sistema de Arquivos
Ferramentas para manipulação de arquivos e pastas no diretório de trabalho
"""

import os
import sys
from pathlib import Path
from typing import Dict


# Diretório de trabalho (mesa_de_trabalho na pasta do projeto)
# Usa o caminho absoluto a partir da localização deste arquivo
DIRETORIO_TRABALHO = Path(__file__).parent.parent / "mesa_de_trabalho"

# Cria o diretório se não existir
try:
    DIRETORIO_TRABALHO.mkdir(exist_ok=True)
    print(f"📂 Diretório de trabalho: {DIRETORIO_TRABALHO.absolute()}", file=sys.stderr)
except Exception as e:
    print(f"⚠️ Erro ao criar diretório de trabalho: {e}", file=sys.stderr)


class FerramentaCriarPasta:
    """Ferramenta para criar pastas"""
    
    @staticmethod
    def nome() -> str:
        return "criar_pasta"
    
    @staticmethod
    def descricao() -> str:
        return "Cria uma nova pasta no diretório de trabalho (mesa_de_trabalho)"
    
    @staticmethod
    def parametros() -> Dict:
        return {
            "nome_pasta": {
                "type": "string",
                "description": "Nome da pasta a criar"
            }
        }
    
    @staticmethod
    def executar(nome_pasta: str) -> str:
        """
        Cria uma pasta
        
        Args:
            nome_pasta: Nome da pasta
        
        Returns:
            Mensagem de sucesso ou erro
        """
        try:
            # Garante que o diretório de trabalho existe
            if not DIRETORIO_TRABALHO.exists():
                DIRETORIO_TRABALHO.mkdir(parents=True, exist_ok=True)
            
            caminho_pasta = DIRETORIO_TRABALHO / nome_pasta
            
            if caminho_pasta.exists():
                return f"❌ A pasta '{nome_pasta}' já existe em: {caminho_pasta.absolute()}"
            
            caminho_pasta.mkdir(parents=True, exist_ok=False)
            
            # Verifica se realmente criou
            if caminho_pasta.exists() and caminho_pasta.is_dir():
                return f"✅ Pasta '{nome_pasta}' criada com sucesso!\n📂 Caminho: {caminho_pasta.absolute()}"
            else:
                return f"⚠️ Pasta não foi criada. Caminho tentado: {caminho_pasta.absolute()}"
            
        except Exception as e:
            return f"❌ Erro ao criar pasta: {str(e)}\n📂 Tentando criar em: {DIRETORIO_TRABALHO.absolute()}/{nome_pasta}"


class FerramentaCriarArquivo:
    """Ferramenta para criar arquivos"""
    
    @staticmethod
    def nome() -> str:
        return "criar_arquivo"
    
    @staticmethod
    def descricao() -> str:
        return "Cria um novo arquivo no diretório de trabalho com conteúdo opcional"
    
    @staticmethod
    def parametros() -> Dict:
        return {
            "nome_arquivo": {
                "type": "string",
                "description": "Nome do arquivo (ex: 'nota.txt', 'codigo.py')"
            },
            "conteudo": {
                "type": "string",
                "description": "Conteúdo do arquivo",
                "default": "",
                "optional": True
            }
        }
    
    @staticmethod
    def executar(nome_arquivo: str, conteudo: str = "") -> str:
        """
        Cria um arquivo
        
        Args:
            nome_arquivo: Nome do arquivo
            conteudo: Conteúdo (opcional)
        
        Returns:
            Mensagem de sucesso ou erro
        """
        try:
            # Garante que o diretório de trabalho existe
            if not DIRETORIO_TRABALHO.exists():
                DIRETORIO_TRABALHO.mkdir(parents=True, exist_ok=True)
            
            caminho_arquivo = DIRETORIO_TRABALHO / nome_arquivo
            
            if caminho_arquivo.exists():
                return f"❌ O arquivo '{nome_arquivo}' já existe em: {caminho_arquivo.absolute()}"
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            # Verifica se realmente criou
            if caminho_arquivo.exists() and caminho_arquivo.is_file():
                tamanho = len(conteudo)
                return f"✅ Arquivo '{nome_arquivo}' criado com sucesso! ({tamanho} caracteres)\n📂 Caminho: {caminho_arquivo.absolute()}"
            else:
                return f"⚠️ Arquivo não foi criado. Caminho tentado: {caminho_arquivo.absolute()}"
            
        except Exception as e:
            return f"❌ Erro ao criar arquivo: {str(e)}\n📂 Tentando criar em: {DIRETORIO_TRABALHO.absolute()}/{nome_arquivo}"


class FerramentaListarArquivos:
    """Ferramenta para listar arquivos e pastas"""
    
    @staticmethod
    def nome() -> str:
        return "listar_arquivos"
    
    @staticmethod
    def descricao() -> str:
        return "Lista arquivos e pastas no diretório de trabalho"
    
    @staticmethod
    def parametros() -> Dict:
        return {
            "pasta": {
                "type": "string",
                "description": "Subpasta para listar (padrão: raiz do diretório de trabalho)",
                "default": ".",
                "optional": True
            }
        }
    
    @staticmethod
    def executar(pasta: str = ".") -> str:
        """
        Lista conteúdo de uma pasta
        
        Args:
            pasta: Caminho da pasta (padrão: raiz)
        
        Returns:
            Lista formatada de arquivos e pastas
        """
        try:
            if pasta == ".":
                caminho = DIRETORIO_TRABALHO
            else:
                caminho = DIRETORIO_TRABALHO / pasta
            
            if not caminho.exists():
                return f"❌ Pasta '{pasta}' não encontrada!"
            
            itens = list(caminho.iterdir())
            
            if not itens:
                return f"📂 A pasta está vazia."
            
            # Separa pastas e arquivos
            pastas = [item for item in itens if item.is_dir()]
            arquivos = [item for item in itens if item.is_file()]
            
            resultado = f"📂 Conteúdo de mesa_de_trabalho/{pasta}:\n\n"
            
            if pastas:
                resultado += "📁 Pastas:\n"
                for pasta_item in sorted(pastas):
                    resultado += f"  - {pasta_item.name}/\n"
                resultado += "\n"
            
            if arquivos:
                resultado += "📄 Arquivos:\n"
                for arquivo in sorted(arquivos):
                    tamanho = arquivo.stat().st_size
                    if tamanho < 1024:
                        tamanho_str = f"{tamanho} bytes"
                    elif tamanho < 1024 * 1024:
                        tamanho_str = f"{tamanho/1024:.1f} KB"
                    else:
                        tamanho_str = f"{tamanho/(1024*1024):.1f} MB"
                    resultado += f"  - {arquivo.name} ({tamanho_str})\n"
            
            return resultado
            
        except Exception as e:
            return f"Erro ao listar arquivos: {str(e)}"


# Classe agregadora para facilitar uso
class FerramentaSistemaArquivos:
    """Agregador das ferramentas de sistema de arquivos"""
    
    @staticmethod
    def obter_todas():
        """Retorna todas as ferramentas de sistema de arquivos"""
        return [
            FerramentaCriarPasta,
            FerramentaCriarArquivo,
            FerramentaListarArquivos
        ]
