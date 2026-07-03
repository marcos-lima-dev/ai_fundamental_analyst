import yfinance as yf
import json

class AgenteColetor:
    def __init__(self):
        # yfinance não precisa de token, então o init fica vazio
        pass

    def buscar_dados(self, ticker: str) -> dict:
        # O Yahoo Finance exige o sufixo .SA para ações brasileiras
        if not ticker.upper().endswith(".SA"):
            ticker_yf = f"{ticker}.SA"
        else:
            ticker_yf = ticker

        try:
            print(f"🔍 Agente 1: Buscando dados para {ticker_yf} no Yahoo Finance...")
            
            # Baixa o objeto do ticker
            acao = yf.Ticker(ticker_yf)
            info = acao.info
            
            # VALIDAÇÃO: Se a API não retornou o nome da empresa ou o preço atual, o ticker não existe!
            if not info or info.get("longName") is None or info.get("regularMarketPrice") is None:
                print(f"❌ Agente 1: Ticker {ticker} não encontrado ou sem dados na bolsa.")
                return None
            
            # Extraímos os dados do dicionário 'info' do Yahoo
            # Usamos .get() para não quebrar se algum dado não existir
            dados_extraidos = {
                "ticker": ticker.upper(),
                "nome": info.get("longName", info.get("shortName", ticker)),
                "setor": info.get("sector", "N/A"),
                
                # Valuation
                "pl": info.get("trailingPE", None),
                "pvp": info.get("priceToBook", None),
                "ev_ebitda": info.get("enterpriseToEbitda", None),
                
                # Rentabilidade
                "roe": info.get("returnOnEquity", None),
                "roic": info.get("returnOnCapital", None), # Yahoo às vezes não tem ROIC
                "margem_liquida": info.get("profitMargins", None),
                
                # Endividamento
                # Yahoo usa Debt/Equity. Podemos adaptar no Agente 3 se necessário.
                "divida_liquida_ebitda": info.get("debtToEquity", None), 
                
                # Dividendos
                "dividend_yield": info.get("dividendYield", None),
                
                # Crescimento
                "crescimento_receita_5a": info.get("revenueGrowth", None),
                "crescimento_lucro_5a": info.get("earningsGrowth", None)
            }

            # Limpeza: Converter decimais para percentuais (ex: 0.25 -> 25)
            chaves_percentuais = ["roe", "margem_liquida", "dividend_yield", "crescimento_receita_5a", "crescimento_lucro_5a"]
            for key in chaves_percentuais:
                valor = dados_extraidos[key]
                if valor is not None and isinstance(valor, (int, float)):
                    # Se vier como decimal (ex: 0.25), multiplica por 100
                    if valor < 1:
                        dados_extraidos[key] = round(valor * 100, 2)

            print(f"✅ Agente 1: Dados de {ticker} coletados com sucesso!")
            return dados_extraidos

        except Exception as err:
            print(f"❌ Erro inesperado ao buscar {ticker}: {err}")
            return None

# Bloco de teste
if __name__ == "__main__":
    coletor = AgenteColetor()
    # Teste com um ticker inexistente para ver a validação funcionando
    ticker_teste = "PETR5"
    dados = coletor.buscar_dados(ticker_teste)
    
    if dados:
        print("\n--- Dados Extraídos ---")
        print(json.dumps(dados, indent=4, ensure_ascii=False))
    else:
        print("\nFalha ao extrair dados. Ticker inválido.")