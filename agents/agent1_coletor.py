import yfinance as yf
import json
from curl_cffi import requests as cffi_requests

class AgenteColetor:
    def __init__(self):
        pass

    def buscar_dados(self, ticker: str) -> dict:
        if not ticker.upper().endswith(".SA"):
            ticker_yf = f"{ticker}.SA"
        else:
            ticker_yf = ticker

        try:
            print(f"🔍 Agente 1: Buscando dados para {ticker_yf} no Yahoo Finance...")
            
            # PLANO C: Usar curl_cffi para "fingir" ser um Chrome real e burlar o 429 do Yahoo
            session = cffi_requests.Session(impersonate="chrome")
            
            acao = yf.Ticker(ticker_yf, session=session)
            info = acao.info
            
            if not info or info.get("longName") is None or info.get("regularMarketPrice") is None:
                print(f"❌ Agente 1: Ticker {ticker} não encontrado ou sem dados na bolsa.")
                return None
            
            dados_extraidos = {
                "ticker": ticker.upper(),
                "nome": info.get("longName", info.get("shortName", ticker)),
                "setor": info.get("sector", "N/A"),
                "pl": info.get("trailingPE", None),
                "pvp": info.get("priceToBook", None),
                "ev_ebitda": info.get("enterpriseToEbitda", None),
                "roe": info.get("returnOnEquity", None),
                "roic": info.get("returnOnCapital", None),
                "margem_liquida": info.get("profitMargins", None),
                "divida_liquida_ebitda": info.get("debtToEquity", None), 
                "dividend_yield": info.get("dividendYield", None),
                "crescimento_receita_5a": info.get("revenueGrowth", None),
                "crescimento_lucro_5a": info.get("earningsGrowth", None)
            }

            chaves_percentuais = ["roe", "margem_liquida", "dividend_yield", "crescimento_receita_5a", "crescimento_lucro_5a"]
            for key in chaves_percentuais:
                valor = dados_extraidos[key]
                if valor is not None and isinstance(valor, (int, float)):
                    if valor < 1:
                        dados_extraidos[key] = round(valor * 100, 2)

            print(f"✅ Agente 1: Dados de {ticker} coletados com sucesso!")
            return dados_extraidos

        except Exception as err:
            print(f"❌ Erro inesperado ao buscar {ticker}: {err}")
            return None

if __name__ == "__main__":
    coletor = AgenteColetor()
    ticker_teste = "PETR4"
    dados = coletor.buscar_dados(ticker_teste)
    if dados:
        print("\n--- Dados Extraídos ---")
        print(json.dumps(dados, indent=4, ensure_ascii=False))