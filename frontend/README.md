from pathlib import Path

readme_content = r"""# 📈 AI Fundamental Analyst

## Seu Copiloto de Análise Fundamentalista com IA

Analise empresas da B3 usando Inteligência Artificial, indicadores financeiros reais e agentes inteligentes.

**Python • FastAPI • Next.js • OpenAI • License**

⭐ **Star this repository** • 🚀 **Follow the development**

> AI Fundamental Analyst Logo

---

# 🚀 Visão Geral

O **AI Fundamental Analyst** é uma aplicação SaaS projetada para ajudar investidores a realizarem análises fundamentalistas de qualidade profissional utilizando Inteligência Artificial.

Em vez de simplesmente exibir tabelas de indicadores financeiros, a aplicação comporta-se como uma equipe de analistas. O sistema garante a filosofia:

> **"Os números vêm do motor determinístico. A interpretação vem da IA."**

Isso elimina alucinações matemáticas e gera relatórios confiáveis.

---

# ✨ Features

- 📊 **Dashboard Premium:** Interface limpa, responsiva e animada com Framer Motion.
- 🤖 **Pipeline Multi-Agente:** 4 agentes especializados trabalhando em sequência.
- 🎯 **Score Fundamentalista:** Avaliação matemática de 0 a 10 baseada em regras clássicas.
- 🩺 **Ficha Médica:** Barras de progresso para Saúde Financeira, Valuation, Crescimento, etc.
- 🧠 **Relatório IA:** Tese de investimento gerada em linguagem natural, didática e acessível.
- 💬 **Chat Contextual:** Tire dúvidas sobre a análise gerada diretamente com a IA.
- 🔎 **Coleta Robusta:** Web scraping do Fundamentus para dados atualizados da B3.

---

# 🧠 Arquitetura Multi-Agente

O coração do backend é um pipeline orquestrado pelo FastAPI, onde cada agente tem uma responsabilidade única:

```text
            [ Requisição do Usuário ]
                       │
                       ▼
        ┌──────────────────────────┐
        │ Agente 1: Coletor        │  <-- Web Scraping (Fundamentus)
        └──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │ Agente 2: Calculador     │  <-- Normalização de Dados
        └──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │ Agente 3: Avaliador      │  <-- Regras Matemáticas e Score
        └──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │ Agente 4: Narrador (IA)  │  <-- GPT-4o-mini (OpenAI)
        └──────────────────────────┘
                       │
                       ▼
        [ Relatório + Chat em JSON ]
🛠️ Tech Stack
Backend
Python 3.11+
FastAPI (Servidor e Rotas)
BeautifulSoup4 (Web Scraping do Fundamentus)
OpenAI API (Agente Narrador)
Pandas / Pydantic (Tratamento de dados)
Frontend
Next.js 14 (React)
Tailwind CSS (Estilização SaaS)
Framer Motion (Animações e Microinterações)
Recharts (Gráfico Radial de Score)
React Markdown (Renderização do relatório IA)
📁 Estrutura do Projeto
ai_fundamental_analyst/
│
├── agents/                # Lógica dos 4 Agentes
│   ├── agent1_coletor.py  # Busca dados no Fundamentus
│   ├── agent3_avaliador.py# Aplica regras e gera o Score
│   └── agent4_narrador.py # Integra com OpenAI para gerar relatório
│
├── frontend/              # Aplicação Next.js
│   ├── app/
│   │   └── page.tsx       # Dashboard principal (UI)
│   └── package.json
│
├── .env                   # Variáveis de ambiente (OPENAI_API_KEY)
├── .gitignore
├── main.py                # Entry point do FastAPI (Orquestrador)
├── requirements.txt       # Dependências Python
└── README.md
⚙️ Instalação e Uso Local
Clone o repositório
git clone https://github.com/marcos-lima-dev/ai_fundamental_analyst.git
cd ai_fundamental_analyst
Configurando o Backend
# Crie seu arquivo .env com a chave:
# OPENAI_API_KEY=sk-...

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
Configurando o Frontend
cd frontend

npm install

npm run dev

Acesse http://localhost:3000 no seu navegador.

🎯 Roadmap
 MVP 1: Motor determinístico e cálculo de scores
 MVP 2: Dashboard Frontend com Gráficos e Chat IA
 Deploy em Produção (Backend no Render, Frontend na Vercel)
 Acordar Backend Automaticamente (Cron Job)
 MVP 3: Comparação de Ações lado a lado
 Análise de Setor (Melhores empresas por segmento)
 Modo Buffett (Analisar segundo princípios de Warren Buffett)
 Upload de Documentos (Relatórios de RI, Formulário de Referência)
💡 Visão

O objetivo não é substituir o investidor.

O objetivo é dar a cada investidor acesso a uma equipe de IA capaz de ler, interpretar e explicar os fundamentos das empresas de forma clara e transparente.

Pense nisso como ter sua própria equipe de equity research digital disponível 24/7.

🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir Issues ou enviar Pull Requests com melhorias para as regras de avaliação, design ou novos agentes.

📜 Licença

Distribuído sob a Licença MIT.

<div align="center">

Made with ❤️ by Marcos S. Lima

</div> """

Path("README.md").write_text(readme_content, encoding="utf-8")

print("✅ README.md criado com sucesso!")