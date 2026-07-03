import requests
from bs4 import BeautifulSoup
import json
import re

class AgenteColetor:
    def __init__(self):
        pass

    def _limpar_valor(self, texto):
        if not texto or texto in ['-', 'N/A', '']:
            return None
        texto = str(texto).replace('.', '').replace(',', '.').replace('%', '').strip()
        try:
            return float(texto)
        except ValueError:
            return None

    def buscar_dados(self, ticker: str) -> dict:
        ticker = ticker.upper()
        url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

        try:
            print(f"🔍 Agente 1: Buscando dados para {ticker} no Fundamentus...")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            labels = soup.find_all('td', class_='label')
            if not labels:
                print(f"❌ Agente 1: Ticker {ticker} não encontrado.")
                return None

            dados_brutos = {}
            for label_td in labels:
                # TRUQUE MESTRE ATUALIZADO: Remove espaços, pontos E O PONTO DE INTERROGAÇÃO !
                label = re.sub(r'[?.\s]', '', label_td.get_text(strip=True).replace('\xa0', ' '))
                value_td = label_td.find_next_sibling('td')
                if value_td:
                    value = value_td.get_text(strip=True).replace('\xa0', ' ')
                    dados_brutos[label] = value

            divida_ratio = self._limpar_valor(dados_brutos.get("DívLíq/Patrim"))
            divida_percent = divida_ratio * 100 if divida_ratio is not None else None

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
                "margem_liquida": self._limpar_valor(dados_brutos.get("MargLíquida")),
                
                # Endividamento
                "divida_liquida_ebitda": divida_percent,
                
                # Dividendos
                "dividend_yield": self._limpar_valor(dados_brutos.get("DivYield")),
                
                # Crescimento
                "crescimento_receita_5a": self._limpar_valor(dados_brutos.get("CresRec(5a)")),
                "crescimento_lucro_5a": self._limpar_valor(dados_brutos.get("CresLuc(5a)"))
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