# 🛠️ Ferramentas MCP - Guia de Desenvolvimento

Pasta de ferramentas modulares para o servidor MCP do JARVIS.

## 📂 Estrutura

```
tools/
├── __init__.py           # Registra todas as ferramentas
├── hora.py              # Ferramenta de hora/data
├── clima.py             # Ferramenta de clima (API wttr.in)
├── buscar_web.py        # Ferramenta de busca (DuckDuckGo API)
├── sistema_arquivos.py  # Ferramentas de arquivos/pastas
└── README.md           # Este arquivo
```

## ✨ Como Criar uma Nova Ferramenta

### 1. Crie um novo arquivo na pasta `tools/`

Exemplo: `tools/minha_ferramenta.py`

```python
"""
Ferramenta: Minha Ferramenta
Descrição do que faz
"""

from typing import Dict


class MinhaFerramenta:
    """Descrição da ferramenta"""

    @staticmethod
    def nome() -> str:
        """Nome da ferramenta (usado para chamá-la)"""
        return "minha_ferramenta"

    @staticmethod
    def descricao() -> str:
        """Descrição para o LLM saber quando usar"""
        return "Faz algo interessante e útil"

    @staticmethod
    def parametros() -> Dict:
        """Define os parâmetros que a ferramenta aceita"""
        return {
            "parametro1": {
                "type": "string",
                "description": "Descrição do parâmetro"
            },
            "parametro2": {
                "type": "number",
                "description": "Outro parâmetro",
                "default": 10,
                "optional": True
            }
        }

    @staticmethod
    def executar(parametro1: str, parametro2: int = 10) -> str:
        """
        Executa a ferramenta

        Args:
            parametro1: Descrição
            parametro2: Descrição (opcional)

        Returns:
            Resultado da operação
        """
        try:
            # Seu código aqui
            resultado = f"Processei {parametro1} com valor {parametro2}"
            return resultado
        except Exception as e:
            return f"Erro: {str(e)}"
```

### 2. Registre no `__init__.py`

Adicione o import e export:

```python
from .minha_ferramenta import MinhaFerramenta

__all__ = [
    'FerramentaHora',
    'FerramentaClima',
    'FerramentaBuscarWeb',
    'FerramentaSistemaArquivos',
    'MinhaFerramenta'  # ← ADICIONE AQUI
]
```

### 3. Registre no `mcp_server.py`

Adicione à lista de ferramentas:

```python
from tools import (
    FerramentaHora,
    FerramentaClima,
    FerramentaBuscarWeb,
    FerramentaSistemaArquivos,
    MinhaFerramenta  # ← ADICIONE AQUI
)

# ...

def _registrar_ferramentas(self):
    classes_ferramentas = [
        FerramentaHora,
        FerramentaClima,
        FerramentaBuscarWeb,
        MinhaFerramenta,  # ← ADICIONE AQUI
    ]
```

### 4. Pronto! 🎉

Sua ferramenta já está disponível e o JARVIS pode usá-la automaticamente!

## 📝 Padrão de Classe

Todas as ferramentas devem seguir este padrão:

- ✅ Métodos estáticos (`@staticmethod`)
- ✅ `nome()` - retorna string com identificador único
- ✅ `descricao()` - retorna string descritiva para o LLM
- ✅ `parametros()` - retorna dicionário com especificação de parâmetros
- ✅ `executar(**kwargs)` - executa a ferramenta e retorna string

## 🎯 Tipos de Parâmetros

### String

```python
"meu_parametro": {
    "type": "string",
    "description": "Descrição clara"
}
```

### Número

```python
"meu_numero": {
    "type": "number",
    "description": "Um número inteiro ou float"
}
```

### Booleano

```python
"meu_bool": {
    "type": "boolean",
    "description": "True ou False"
}
```

### Opcional (com valor padrão)

```python
"opcional": {
    "type": "string",
    "description": "Parâmetro opcional",
    "default": "valor_padrao",
    "optional": True
}
```

## 💡 Dicas

### ✅ Faça

- Use nomes descritivos em português
- Documente bem os parâmetros
- Retorne sempre string (facilita exibição)
- Trate exceções dentro do `executar()`
- Use tipos simples (str, int, float, bool)

### ❌ Evite

- Operações longas (> 5 segundos)
- Parâmetros complexos (listas, objetos aninhados)
- Efeitos colaterais sem avisar o usuário
- Retornar objetos complexos

## 🔍 Exemplos Práticos

### Ferramenta Simples (sem API)

```python
class FerramentaContadorPalavras:
    @staticmethod
    def nome() -> str:
        return "contar_palavras"

    @staticmethod
    def descricao() -> str:
        return "Conta quantas palavras tem um texto"

    @staticmethod
    def parametros() -> Dict:
        return {
            "texto": {
                "type": "string",
                "description": "Texto para contar palavras"
            }
        }

    @staticmethod
    def executar(texto: str) -> str:
        palavras = len(texto.split())
        return f"O texto tem {palavras} palavras."
```

### Ferramenta com API Externa

```python
import requests

class FerramentaCotacaoDolar:
    @staticmethod
    def nome() -> str:
        return "cotacao_dolar"

    @staticmethod
    def descricao() -> str:
        return "Obtém cotação atual do dólar"

    @staticmethod
    def parametros() -> Dict:
        return {}  # Sem parâmetros

    @staticmethod
    def executar() -> str:
        try:
            url = "https://api.exemplo.com/cotacao"
            resposta = requests.get(url, timeout=5)
            dados = resposta.json()
            valor = dados['USD']['valor']
            return f"Dólar: R$ {valor:.2f}"
        except Exception as e:
            return f"Erro ao buscar cotação: {str(e)}"
```

### Ferramenta com Múltiplos Parâmetros

```python
class FerramentaCalculadoraIMC:
    @staticmethod
    def nome() -> str:
        return "calcular_imc"

    @staticmethod
    def descricao() -> str:
        return "Calcula o IMC (Índice de Massa Corporal)"

    @staticmethod
    def parametros() -> Dict:
        return {
            "peso": {
                "type": "number",
                "description": "Peso em kg"
            },
            "altura": {
                "type": "number",
                "description": "Altura em metros"
            }
        }

    @staticmethod
    def executar(peso: float, altura: float) -> str:
        imc = peso / (altura ** 2)

        if imc < 18.5:
            categoria = "Abaixo do peso"
        elif imc < 25:
            categoria = "Peso normal"
        elif imc < 30:
            categoria = "Sobrepeso"
        else:
            categoria = "Obesidade"

        return f"IMC: {imc:.1f} - {categoria}"
```

## 🚀 Ideias de Novas Ferramentas

- 📧 Enviar email
- 💱 Conversão de moedas
- 🌡️ Conversão de unidades (temperatura, distância, etc)
- 📝 Gerador de senhas
- 🎲 Números aleatórios
- 📅 Cálculos de data (dias entre datas, idade, etc)
- 🔗 Encurtador de URLs
- 🖼️ Download de imagens
- 📊 Gerador de gráficos simples
- 🎵 Controle de música do sistema

---

Desenvolvido com ❤️ para facilitar a extensão do JARVIS!
