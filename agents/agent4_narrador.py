import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AgenteNarrador:
    def __init__(self):
        # Inicializa o cliente da OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini" # Rápido, barato e excelente para interpretação de dados

    def gerar_relatorio(self, dados_avaliados: dict) -> str:
        print(f"🧠 Agente 4: Gerando relatório narrativo para {dados_avaliados.get('ticker')}...")

        system_prompt = """Você é o "AI Fundamental Analyst", um copiloto de investimentos focado em ajudar investidores iniciantes e intermediários. 
Sua missão é receber dados financeiros estruturados (JSON) já calculados e pontuados pelo sistema e transformá-los em uma análise clara, didática e conversacional.

REGRAS RÍGIDAS:
1. NUNCA invente números. Use EXCLUSIVAMENTE os dados fornecidos no JSON.
2. NUNCA faça cálculos matemáticos. O sistema já fez isso por você.
3. Seja didático. Se mencionar um indicador (ex: ROE), explique brevemente o que ele significa na prática.
4. Tom: Profissional, acolhedor, objetivo. Sem jargões complexos não explicados.
5. Não dê recomendação de "comprar" ou "vender". Apenas analise a saúde financeira, valuation e riscos.

FORMATO DA SUA RESPOSTA:
1. 🩺 Diagnóstico Geral (1 parágrafo)
- Um resumo direto ao ponto sobre a saúde da empresa, mencionando o Score Final.
2. 💪 Pontos Fortes (Bullet points)
- Liste as 2 ou 3 maiores qualidades da empresa baseadas nas notas mais altas e nos dados_brutos.
3. ⚠️ Pontos de Atenção (Bullet points)
- Liste os 1 ou 2 principais riscos ou pontos fracos baseados nas notas mais baixas e nos dados_brutos.
4. 💬 Explicação para Iniciantes (1 parágrafo curto)
- Resuma a análise como se estivesse explicando para uma pessoa de 15 anos, usando uma analogia simples do dia a dia (ex: comprar uma padaria, um carro, etc)."""

        # Converte o dicionário para string JSON para enviar à IA
        user_prompt = f"Aqui estão os dados da empresa. Gere a análise:\n\n{json.dumps(dados_avaliados, indent=4, ensure_ascii=False)}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5 # Um pouco de criatividade, mas focado nos fatos
            )
            
            relatorio = response.choices[0].message.content
            print("✅ Agente 4: Relatório gerado!")
            return relatorio

        except Exception as err:
            return f"❌ Erro ao gerar relatório: {err}"

    def responder_pergunta(self, dados_avaliados: dict, pergunta: str) -> str:
        print(f"🧠 Agente 4: Respondendo pergunta do usuário...")
        
        system_prompt = """Você é o "AI Fundamental Analyst", um copiloto de investimentos. 
O usuário fez uma pergunta sobre uma empresa que ele acabou de analisar.
Use EXCLUSIVAMENTE os dados financeiros fornecidos no JSON para responder.
Seja didático, direto e não invente números. Se a pergunta fugir do tema financeiro ou dos dados fornecidos, diga que só pode responder sobre a análise atual."""

        user_prompt = f"Dados da análise:\n{json.dumps(dados_avaliados, indent=4, ensure_ascii=False)}\n\nPergunta do usuário: {pergunta}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as err:
            return f"❌ Erro ao responder: {err}"

# Bloco de teste integrado (Agente 1 -> Agente 3 -> Agente 4)
if __name__ == "__main__":
    from agent1_coletor import AgenteColetor
    from agent3_avaliador import AgenteAvaliador
    
    coletor = AgenteColetor()
    avaliador = AgenteAvaliador()
    narrador = AgenteNarrador()
    
    ticker_teste = "PETR4"
    
    # 1. Coleta
    dados_brutos = coletor.buscar_dados(ticker_teste)
    
    if dados_brutos:
        # 2. Avalia
        resultado_final = avaliador.avaliar(dados_brutos)
        
        # 3. Narra
        relatorio = narrador.gerar_relatorio(resultado_final)
        
        print("\n" + "="*50)
        print("📄 RELATÓRIO FINAL DA IA")
        print("="*50)
        print(relatorio)