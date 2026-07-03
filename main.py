from fastapi import FastAPI, HTTPException
from agents.agent1_coletor import AgenteColetor
from agents.agent3_avaliador import AgenteAvaliador
from agents.agent4_narrador import AgenteNarrador

app = FastAPI(title="AI Fundamental Analyst API")

# Inicializa os agentes uma única vez
coletor = AgenteColetor()
avaliador = AgenteAvaliador()
narrador = AgenteNarrador()

@app.get("/")
def read_root():
    return {"message": "AI Fundamental Analyst API está no ar! Use /docs para testar."}

@app.get("/analisar/{ticker}")
def analisar_acao(ticker: str):
    """
    Endpoint principal que recebe o ticker (ex: PETR4) e retorna a análise completa.
    """
    ticker = ticker.upper()
    
    # 1. Agente 1: Coleta dados
    dados_brutos = coletor.buscar_dados(ticker)
    if not dados_brutos:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar dados para o ticker {ticker}")

    # 2. Agente 3: Avalia e gera score
    dados_avaliados = avaliador.avaliar(dados_brutos)
    
    # 3. Agente 4: Gera relatório em linguagem natural
    relatorio_ia = narrador.gerar_relatorio(dados_avaliados)
    
    # Retorna um JSON com os dados estruturados + o texto da IA
    return {
        "ticker": ticker,
        "score_final": dados_avaliados["score_final"],
        "detalhes": dados_avaliados["detalhes"],
        "relatorio_ia": relatorio_ia
    }