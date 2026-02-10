"""
Ferramenta: Hora e Data
Retorna informações sobre hora e data atual
"""

from datetime import datetime
from typing import Dict, List


class FerramentaHora:
    """Ferramenta para obter hora e data atual"""
    
    @staticmethod
    def nome() -> str:
        return "obter_hora"
    
    @staticmethod
    def descricao() -> str:
        return "Retorna a hora/data atual em diferentes formatos"
    
    @staticmethod
    def parametros() -> Dict:
        return {
            "formato": {
                "type": "string",
                "description": "Formato: 'completo' (data e hora), 'hora' (só hora), 'data' (só data)",
                "default": "completo",
                "optional": True
            }
        }
    
    @staticmethod
    def executar(formato: str = "completo") -> str:
        """
        Executa a ferramenta
        
        Args:
            formato: "completo", "hora" ou "data"
        
        Returns:
            String formatada com hora/data
        """
        agora = datetime.now()
        
        if formato == "hora":
            return agora.strftime("%H:%M:%S")
        elif formato == "data":
            return agora.strftime("%d/%m/%Y")
        else:  # completo
            return agora.strftime("%d/%m/%Y às %H:%M:%S")
