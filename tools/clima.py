"""
Ferramenta: Clima
Obtém informações de clima em tempo real usando API wttr.in
"""

import requests
from typing import Dict


class FerramentaClima:
    """Ferramenta para obter clima em tempo real"""
    
    @staticmethod
    def nome() -> str:
        return "obter_clima"
    
    @staticmethod
    def descricao() -> str:
        return "Retorna informações de clima em tempo real usando API wttr.in (gratuita)"
    
    @staticmethod
    def parametros() -> Dict:
        return {
            "cidade": {
                "type": "string",
                "description": "Nome da cidade",
                "default": "São Paulo",
                "optional": True
            }
        }
    
    @staticmethod
    def executar(cidade: str = "São Paulo") -> str:
        """
        Executa a ferramenta
        
        Args:
            cidade: Nome da cidade
        
        Returns:
            Informações de clima
        """
        try:
            # API wttr.in - não precisa de chave!
            url = f"https://wttr.in/{cidade}?format=%C+%t+%h+%w"
            headers = {'User-Agent': 'curl/7.68.0'}
            
            resposta = requests.get(url, headers=headers, timeout=5)
            
            if resposta.status_code == 200:
                # Formato: "Condição Temperatura Umidade Vento"
                clima = resposta.text.strip()
                return f"Clima em {cidade}: {clima}"
            else:
                return f"Não consegui obter o clima de {cidade} no momento."
                
        except Exception as e:
            return f"Erro ao buscar clima: {str(e)}"
