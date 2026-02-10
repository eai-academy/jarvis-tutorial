"""
Sistema de Memória do JARVIS v5
Gerencia configurações do usuário e histórico de conversas usando SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class JarvisMemoria:
    """
    Gerencia a memória persistente do JARVIS
    
    - Configurações do usuário (nome, preferências)
    - Histórico de conversas (últimas N mensagens)
    - Contexto entre sessões
    """
    
    def __init__(self, db_path="jarvis_memoria.db"):
        """
        Inicializa o sistema de memória
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias se não existirem"""
        
        # Tabela de configurações
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de histórico de conversas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de sessões (para estatísticas)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TEXT DEFAULT CURRENT_TIMESTAMP,
                fim TEXT,
                total_mensagens INTEGER DEFAULT 0
            )
        """)
        
        self.conn.commit()
    
    # ========== CONFIGURAÇÕES ==========
    
    def salvar_config(self, chave: str, valor: str):
        """Salva uma configuração"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO configuracoes (chave, valor, data_atualizacao)
            VALUES (?, ?, ?)
        """, (chave, valor, datetime.now().isoformat()))
        self.conn.commit()
    
    def obter_config(self, chave: str, padrao: str = None) -> Optional[str]:
        """Obtém uma configuração"""
        self.cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else padrao
    
    def tem_config(self, chave: str) -> bool:
        """Verifica se uma configuração existe"""
        return self.obter_config(chave) is not None
    
    # ========== NOME DO USUÁRIO ==========
    
    def salvar_nome_usuario(self, nome: str):
        """Salva o nome do usuário"""
        self.salvar_config("nome_usuario", nome)
        print(f"✅ Nome '{nome}' salvo na memória")
    
    def obter_nome_usuario(self) -> Optional[str]:
        """Obtém o nome do usuário"""
        return self.obter_config("nome_usuario")
    
    def tem_nome_usuario(self) -> bool:
        """Verifica se já tem nome do usuário salvo"""
        return self.tem_config("nome_usuario")
    
    # ========== HISTÓRICO DE CONVERSAS ==========
    
    def adicionar_mensagem(self, role: str, content: str):
        """
        Adiciona uma mensagem ao histórico
        
        Args:
            role: "user", "assistant" ou "system"
            content: conteúdo da mensagem
        """
        self.cursor.execute("""
            INSERT INTO historico (role, content, timestamp)
            VALUES (?, ?, ?)
        """, (role, content, datetime.now().isoformat()))
        self.conn.commit()
    
    def obter_historico_recente(self, limite: int = 10) -> List[Dict[str, str]]:
        """
        Obtém as últimas N mensagens do histórico
        
        Args:
            limite: número máximo de mensagens
        
        Returns:
            Lista de dicionários com role e content
        """
        self.cursor.execute("""
            SELECT role, content FROM historico
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))
        
        mensagens = self.cursor.fetchall()
        # Inverte para ordem cronológica (mais antiga primeiro)
        return [{"role": role, "content": content} for role, content in reversed(mensagens)]
    
    def limpar_historico(self):
        """Limpa todo o histórico de conversas"""
        self.cursor.execute("DELETE FROM historico")
        self.conn.commit()
        print("🗑️ Histórico de conversas limpo")
    
    def obter_resumo_historico(self) -> Dict:
        """Obtém estatísticas do histórico"""
        self.cursor.execute("SELECT COUNT(*) FROM historico")
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM historico WHERE role = 'user'")
        total_usuario = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT MIN(timestamp) FROM historico")
        primeira = self.cursor.fetchone()[0]
        
        return {
            "total_mensagens": total,
            "mensagens_usuario": total_usuario,
            "primeira_mensagem": primeira
        }
    
    # ========== SESSÕES ==========
    
    def iniciar_sessao(self) -> int:
        """Inicia uma nova sessão e retorna o ID"""
        self.cursor.execute("""
            INSERT INTO sessoes (inicio) VALUES (?)
        """, (datetime.now().isoformat(),))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def finalizar_sessao(self, sessao_id: int, total_mensagens: int):
        """Finaliza uma sessão"""
        self.cursor.execute("""
            UPDATE sessoes 
            SET fim = ?, total_mensagens = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), total_mensagens, sessao_id))
        self.conn.commit()
    
    def obter_total_sessoes(self) -> int:
        """Retorna o número total de sessões"""
        self.cursor.execute("SELECT COUNT(*) FROM sessoes")
        return self.cursor.fetchone()[0]
    
    # ========== UTILITÁRIOS ==========
    
    def obter_saudacao_contextual(self, nome: str = None) -> str:
        """
        Gera uma saudação apropriada para o horário
        
        Args:
            nome: nome do usuário (opcional)
        
        Returns:
            Saudação formatada
        """
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            periodo = "Bom dia"
        elif 12 <= hora < 18:
            periodo = "Boa tarde"
        else:
            periodo = "Boa noite"
        
        if nome:
            return f"{periodo}, {nome}!"
        else:
            return f"{periodo}!"
    
    def e_primeira_vez(self) -> bool:
        """Verifica se é a primeira vez que o JARVIS está sendo usado"""
        return self.obter_total_sessoes() == 0
    
    def exportar_historico(self, arquivo: str = "historico_jarvis.txt"):
        """Exporta o histórico para um arquivo de texto"""
        historico = self.obter_historico_recente(limite=1000)
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("HISTÓRICO DE CONVERSAS - JARVIS\n")
            f.write("=" * 60 + "\n\n")
            
            for msg in historico:
                role = msg["role"].upper()
                content = msg["content"]
                f.write(f"[{role}]\n{content}\n\n")
        
        print(f"📝 Histórico exportado para {arquivo}")
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        self.conn.close()
    
    def __del__(self):
        """Garante que a conexão seja fechada"""
        try:
            self.conn.close()
        except:
            pass


# Teste rápido
if __name__ == "__main__":
    print("🧪 Testando sistema de memória...")
    
    memoria = JarvisMemoria("teste_memoria.db")
    
    # Testa configurações
    memoria.salvar_nome_usuario("João")
    print(f"Nome: {memoria.obter_nome_usuario()}")
    
    # Testa histórico
    memoria.adicionar_mensagem("user", "Olá JARVIS")
    memoria.adicionar_mensagem("assistant", "Olá! Como posso ajudar?")
    
    historico = memoria.obter_historico_recente(5)
    print(f"Histórico: {len(historico)} mensagens")
    
    # Testa saudação
    print(memoria.obter_saudacao_contextual("João"))
    
    memoria.fechar()
    print("✅ Teste concluído!")
