import requests
from bs4 import BeautifulSoup
import json

class AgenteColetor:
    def __init__(self):
        pass

    def _limpar_valor(self, texto):
        """Converte texto do Fundamentus (ex: '4,67', '10,30%') para número (4.67, 10.30)"""
        if not texto or texto == '-' or texto == 'N/A':
            return None
        # Remove pontos de milhar, troca vírgula por ponto e remove o símbolo de %
        texto = texto.replace('.', '').replace(',', '.').replace('%', '')
        try:
            return float(texto)
        except ValueError:
            return None

    def buscar_dados(self, ticker: str) -> dict:
        ticker = ticker.upper()
        url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            print(f"🔍 Agente 1: Buscando dados para {ticker} no Fundamentus...")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Agente 1: Erro {response.status_code} ao acessar Fundamentus.")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'w728'})
            
            if not table:
                print(f"❌ Agente 1: Ticker {ticker} não encontrado no Fundamentus.")
                return None

            dados_brutos = {}
            # O Fundamentus usa tabelas com 4 colunas (label, valor, label, valor)
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 4:
                    label1 = cells[0].text.strip()
                    value1 = cells[1].text.strip()
                    label2 = cells[2].text.strip()
                    value2 = cells[3].text.strip()
                    dados_brutos[label1] = value1
                    dados_brutos[label2] = value2
                elif len(cells) == 2:
                    label1 = cells[0].text.strip()
                    value1 = cells[1].text.strip()
                    dados_brutos[label1] = value1

            # Validando se o ticker digitado é o mesmo que apareceu na tela
            if "Papel" not in dados_brutos or dados_brutos.get("Papel") != ticker:
                print(f"❌ Agente 1: Ticker {ticker} inválido.")
                return None

            # Mapeando os nomes do Fundamentus para o nosso padrão
            dados_extraidos = {
                "ticker": ticker,
                "nome": dados_brutos.get("Empresa", ticker),
                "setor": dados_brutos.get("Setor", "N/A"),
                
                # Valuation
                "pl": self._limpar_valor(dados_brutos.get("P/L")),
                "pvp": self._limpar_valor(dados_brutos.get("P/VP")),
                "ev_ebitda": self._limpar_valor(dados_brutos.get("EV/EBITDA")),
                
                # Rentabilidade
                "roe": self._limpar_valor(dados_brutos.get("ROE")),
                "roic": self._limpar_valor(dados_brutos.get("ROIC")),
                "margem_liquida": self._limpar_valor(dados_brutos.get("Marg. Líquida")),
                
                # Endividamento (Dív.Br/Patrim é equivalente ao Debt/Equity que usávamos)
                "divida_liquida_ebitda": self._limpar_valor(dados_brutos.get("Dív.Br/Patrim")),
                
                # Dividendos
                "dividend_yield": self._limpar_valor(dados_brutos.get("Div.Yield")),
                
                # Crescimento
                "crescimento_receita_5a": self._limpar_valor(dados_brutos.get("Cres. Rec (5a)")),
                "crescimento_lucro_5a": self._limpar_valor(dados_brutos.get("Cres. Luc (5a)"))
            }

            print(f"✅ Agente 1: Dados de {ticker} coletados com sucesso!")
            return dados_extraidos

        except Exception as err:
            print(f"❌ Erro inesperado ao buscar {ticker}: {err}")
            return None

if __name__ == "__main__":
    coletor = AgenteColetor()
    dados = coletor.buscar_dados("PETR4")
    if dados:
        print(json.dumps(dados, indent=4, ensure_ascii=False))