import requests
from bs4 import BeautifulSoup
import json

class AgenteColetor:
    def __init__(self):
        pass

    def _limpar_valor(self, texto):
        """Converte texto do Fundamentus (ex: '4,67', '10,30%') para número (4.67, 10.30)"""
        if not texto or texto in ['-', 'N/A', '']:
            return None
        # Remove pontos de milhar, troca vírgula por ponto e remove o símbolo de %
        texto = str(texto).replace('.', '').replace(',', '.').replace('%', '').strip()
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
            
            # NOVA LÓGICA ROBUSTA: Encontrar todas as células que são rótulos (labels)
            labels = soup.find_all('td', class_='label')
            if not labels:
                print(f"❌ Agente 1: Ticker {ticker} não encontrado ou site mudou de estrutura.")
                return None

            dados_brutos = {}
            for label_td in labels:
                # O texto do rótulo
                label = label_td.get_text(strip=True).replace('\xa0', ' ')
                # O valor está na próxima célula irmã (td)
                value_td = label_td.find_next_sibling('td')
                if value_td:
                    value = value_td.get_text(strip=True).replace('\xa0', ' ')
                    dados_brutos[label] = value

            # Tratamento do Endividamento (Fundamentus manda como ratio ex: 0.83, multiplicamos por 100 para bater com as regras do Agente 3)
            divida_ratio = self._limpar_valor(dados_brutos.get("Dív.Br/Patrim"))
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
                "margem_liquida": self._limpar_valor(dados_brutos.get("Marg. Líquida")),
                
                # Endividamento
                "divida_liquida_ebitda": divida_percent,
                
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