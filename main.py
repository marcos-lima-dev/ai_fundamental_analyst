from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.agent1_coletor import AgenteColetor
from agents.agent3_avaliador import AgenteAvaliador
from agents.agent4_narrador import AgenteNarrador

app = FastAPI(title="AI Fundamental Analyst API")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, trocar * pela URL do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa os agentes uma única vez
coletor = AgenteColetor()
avaliador = AgenteAvaliador()
narrador = AgenteNarrador()

# Modelo para receber a pergunta do Frontend
class PerguntaRequest(BaseModel):
    pergunta: str
    dados_avaliados: dict

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
        "nome": dados_avaliados.get("nome"),
        "setor": dados_avaliados["dados_brutos"].get("setor", "N/A"),
        "score_final": dados_avaliados["score_final"],
        "detalhes": dados_avaliados["detalhes"],
        "indicadores": {
            "P/L": dados_avaliados["dados_brutos"].get("pl"),
            "P/VP": dados_avaliados["dados_brutos"].get("pvp"),
            "ROE": dados_avaliados["dados_brutos"].get("roe"),
            "Margem Líq.": dados_avaliados["dados_brutos"].get("margem_liquida"),
            "Div. Yield": dados_avaliados["dados_brutos"].get("dividend_yield"),
        },
        "relatorio_ia": relatorio_ia
    }

@app.post("/chat")
def chat_ia(req: PerguntaRequest):
    """
    Endpoint que recebe uma pergunta do usuário e os dados da análise,
    e retorna a resposta da IA baseada estritamente nesses dados.
    """
    resposta = narrador.responder_pergunta(req.dados_avaliados, req.pergunta)
    return {"resposta": resposta}