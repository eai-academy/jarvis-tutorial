"""
Ferramenta: Buscar Web
Realiza buscas na web usando Perplexity AI

IMPORTANTE: 
1. Instale: pip install perplexity-python
2. Adicione no arquivo .env:
   PERPLEXITY_API_KEY=sua_chave_aqui
"""

import os
from perplexity import Perplexity
from typing import Dict


class FerramentaBuscarWeb:
    """Ferramenta para buscar informações atualizadas na web com Perplexity"""
    
    @staticmethod
    def nome() -> str:
        return "buscar_web"
    
    @staticmethod
    def descricao() -> str:
        return "Busca informações atualizadas na web sobre qualquer assunto usando Perplexity AI"
    
    @staticmethod
    def parametros() -> Dict:
        return {
            "consulta": {
                "type": "string",
                "description": "Pergunta ou termo para buscar na web"
            }
        }
    
    @staticmethod
    def executar(consulta: str) -> str:
        """
        Busca informações na web usando Perplexity
        
        Args:
            consulta: Pergunta ou termo de busca
        
        Returns:
            Resposta com links e títulos encontrados
        """
        try:
            # Pega a chave da API do ambiente
            chave_api = os.getenv("PERPLEXITY_API_KEY")
            
            if not chave_api:
                return "❌ Erro: PERPLEXITY_API_KEY não configurada no arquivo .env"
            
            # Configura o cliente Perplexity
            os.environ["PERPLEXITY_API_KEY"] = chave_api
            cliente = Perplexity()
            
            # Faz a busca
            busca = cliente.search.create(query=[consulta], 
                                          max_results=5,
                                          max_tokens_per_page=4096)
            
            # Monta o resultado com os primeiros 5 resultados
            if not busca.results:
                return f"Não encontrei resultados para '{consulta}'"
            
            resultado = f"🌐 Resultados para '{consulta}':\n\n"
            
            for i, item in enumerate(busca.results[:5], 1):
                resultado += f"{i}. {item.title}\n"
                resultado += f"   🔗 {item.url}\n\n"
            
            return resultado.strip()
            
        except Exception as e:
            return f"❌ Erro na busca web: {str(e)}"


