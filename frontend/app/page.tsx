"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { motion, AnimatePresence } from "framer-motion";
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";

interface Detalhe { nota: number; classificacao: string; }
interface Indicadores { "P/L": number | null; "P/VP": number | null; "ROE": number | null; "Margem Líq.": number | null; "Div. Yield": number | null; }
interface AnaliseResponse {
  ticker: string; nome: string; setor: string; score_final: number;
  detalhes: { rentabilidade: Detalhe; valuation: Detalhe; crescimento: Detalhe; endividamento: Detalhe; dividendos: Detalhe; };
  indicadores: Indicadores; relatorio_ia: string;
}

interface MensagemChat {
  role: "user" | "ai";
  content: string;
}

// Definição das etapas da barra de progresso
const ETAPAS_AGENTES = [
  { id: 1, nome: "Coletando Dados" },
  { id: 2, nome: "Calculando Indicadores" },
  { id: 3, nome: "Gerando Análise IA" },
  { id: 4, nome: "Concluído" }
];

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [analise, setAnalise] = useState<AnaliseResponse | null>(null);
  const [erro, setErro] = useState("");

  // Estado da barra de progresso (0 = oculta, 1 a 4 = etapas)
  const [etapaAtual, setEtapaAtual] = useState(0);

  // Estados do Chat
  const [pergunta, setPergunta] = useState("");
  const [chatHistorico, setChatHistorico] = useState<MensagemChat[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  const isTickerValido = ticker.trim().length >= 4;

  // Efeito para simular o avanço dos agentes enquanto a API processa
  useEffect(() => {
    let timer1: any, timer2: any, timer3: any;
    
    if (loading) {
      setEtapaAtual(1); // Inicia na etapa 1
      timer1 = setTimeout(() => setEtapaAtual(2), 800);  // Vai pra etapa 2 em 0.8s
      timer2 = setTimeout(() => setEtapaAtual(3), 2000); // Vai pra etapa 3 em 2.0s
    } else {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    }

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [loading]);

  const buscarAnalise = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isTickerValido) {
      setErro("Digite um ticker válido (mínimo 4 letras). Ex: PETR4");
      return;
    }

    setLoading(true);
    setAnalise(null);
    setErro("");
    setChatHistorico([]);

    try {
      
      const response = await fetch(`https://ai-fundamental-api.onrender.com/analisar/${ticker.trim().toUpperCase()}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Não foi possível concluir a análise.");
      }
      
      const data = await response.json();
      
      // Quando a API responde, pulamos direto para a etapa final
      setEtapaAtual(4);
      
      // Tempo para o usuário ver o "Concluído" antes de a barra sumir lentamente
      setTimeout(() => {
        setEtapaAtual(0);
        setAnalise(data);
      }, 1000);
      
    } catch (err: any) {
      setEtapaAtual(0);
      if (err.message === "Failed to fetch") {
        setErro("Ocorreu um erro de conexão. Tente novamente em alguns instantes.");
      } else {
        setErro(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const limparTudo = () => {
    setTicker("");
    setAnalise(null);
    setErro("");
    setChatHistorico([]);
    setPergunta("");
    setEtapaAtual(0);
  };

  const enviarPergunta = async (textoPergunta: string) => {
    if (!textoPergunta.trim() || !analise) return;
    
    setChatLoading(true);
    const novaMensagemUser: MensagemChat = { role: "user", content: textoPergunta };
    setChatHistorico((prev) => [...prev, novaMensagemUser]);
    setPergunta("");

    try {
      const response = await fetch("https://ai-fundamental-api.onrender.com/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: textoPergunta, dados_avaliados: analise })
      });
      const data = await response.json();
      const novaMensagemAI: MensagemChat = { role: "ai", content: data.resposta };
      setChatHistorico((prev) => [...prev, novaMensagemAI]);
    } catch (err) {
      setChatHistorico((prev) => [...prev, { role: "ai", content: "Erro ao conectar com a IA." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const getCorNota = (nota: number) => nota >= 8 ? "#10b981" : nota >= 5 ? "#f59e0b" : "#f43f5e";
  const getCorTexto = (nota: number) => nota >= 8 ? "text-emerald-600" : nota >= 5 ? "text-amber-600" : "text-rose-600";

  const BarraScore = ({ nome, detalhe, index }: { nome: string, detalhe: Detalhe, index: number }) => (
    <div className="mb-5">
      <div className="flex justify-between items-end mb-1.5">
        <span className="text-sm font-medium text-slate-600">{nome}</span>
        <div className="text-right">
          <span className={`text-base font-bold ${getCorTexto(detalhe.nota)}`}>{detalhe.nota.toFixed(1)}</span>
          <span className="text-xs text-slate-400 ml-1">{detalhe.classificacao}</span>
        </div>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
        <motion.div className="h-2.5 rounded-full" style={{ backgroundColor: getCorNota(detalhe.nota) }} initial={{ width: 0 }} animate={{ width: `${detalhe.nota * 10}%` }} transition={{ duration: 0.8, delay: index * 0.1, ease: "easeOut" }} />
      </div>
    </div>
  );

  const MiniCard = ({ titulo, valor, sufixo = "" }: { titulo: string, valor: number | null, sufixo?: string }) => (
    <motion.div className="bg-slate-50 border border-slate-100 rounded-xl p-4 transition-all hover:shadow-md hover:-translate-y-0.5 hover:bg-white" whileHover={{ scale: 1.02 }}>
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{titulo}</p>
      <p className="text-xl font-bold text-slate-800 mt-1">{valor !== null ? `${valor.toFixed(2)}${sufixo}` : "N/A"}</p>
    </motion.div>
  );

  const scoreData = [{ name: "Score", value: analise?.score_final || 0, fill: "#0f172a" }];

  return (
    <main className="min-h-screen bg-slate-50 text-slate-800 p-4 sm:p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-col sm:flex-row justify-between items-center mb-10">
          <div className="flex items-center gap-3 mb-4 sm:mb-0">
            {/* Adicionando a logo aqui */}
            <img src="/logo.png" alt="AI Fundamental Analyst Logo" className="h-12 w-12 rounded-lg" />
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight leading-none">
                AI Fundamental Analyst
              </h1>
              {/* Corrigindo o texto de "guilada" para "guiada" */}
              <p className="text-slate-500 text-sm mt-1">Análise de ações guiada por inteligência artificial.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-full text-sm font-medium border border-emerald-100">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span> IA Ativa
          </div>
        </header>

        <form onSubmit={buscarAnalise} className="flex flex-col sm:flex-row gap-2 mb-4 max-w-xl mx-auto">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="Digite o ticker (ex: PETR4)"
            className="flex-1 p-4 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-900 focus:outline-none uppercase text-gray-900 shadow-sm font-medium"
          />
          <button 
            type="submit" 
            disabled={loading || !isTickerValido} 
            className="px-8 py-4 bg-slate-900 text-white font-medium rounded-xl hover:bg-slate-800 disabled:bg-slate-400 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {loading ? "Analisando..." : "Analisar"}
          </button>
          
          {(analise || ticker) && (
            <button 
              type="button" 
              onClick={limparTudo} 
              className="px-6 py-4 bg-white border border-slate-200 text-slate-600 font-medium rounded-xl hover:bg-slate-100 hover:text-slate-900 transition-colors shadow-sm"
            >
              Limpar
            </button>
          )}
        </form>
        
        {erro && <p className="text-rose-500 text-center text-sm mb-4 max-w-xl mx-auto">{erro}</p>}

        {/* BARRA DE PROGRESSO DOS AGENTES COM FADE OUT SLOW */}
        <AnimatePresence>
          {etapaAtual > 0 && (
            <motion.div 
              className="max-w-xl mx-auto mb-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 overflow-hidden"
              initial={{ opacity: 0, height: 0, marginBottom: 0 }}
              animate={{ opacity: 1, height: "auto", marginBottom: 32 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              transition={{ duration: 1, ease: "easeInOut" }}
            >
              <div className="flex justify-between items-center relative">
                {/* Linha de fundo da barra */}
                <div className="absolute top-5 left-0 w-full h-1 bg-slate-100 rounded-full -z-0">
                  <motion.div 
                    className="h-full bg-emerald-500 rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: `${((etapaAtual - 1) / (ETAPAS_AGENTES.length - 1)) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>

                {ETAPAS_AGENTES.map((etapa) => (
                  <div key={etapa.id} className="flex flex-col items-center relative z-10 w-1/4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                      etapaAtual > etapa.id ? 'bg-emerald-500 border-emerald-500 text-white' : 
                      etapaAtual === etapa.id ? 'bg-slate-900 border-slate-900 text-white scale-110' : 
                      'bg-white border-slate-200 text-slate-400'
                    }`}>
                      {etapaAtual > etapa.id ? '✓' : etapa.id}
                    </div>
                    <span className={`mt-2 text-xs font-medium text-center transition-colors ${etapaAtual >= etapa.id ? 'text-slate-900' : 'text-slate-400'}`}>
                      {etapa.nome}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {analise && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <motion.div className="lg:col-span-1 space-y-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center">
                <div className="text-center mb-2 w-full border-b pb-4">
                  <p className="text-xl font-bold text-slate-900">{analise.ticker}</p>
                  <p className="text-xs text-slate-400 truncate">{analise.nome}</p>
                </div>
                <div className="relative w-40 h-40 my-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="75%" outerRadius="100%" data={scoreData} startAngle={90} endAngle={-270}>
                      <PolarAngleAxis type="number" domain={[0, 10]} angleAxisId={0} tick={false} />
                      <RadialBar background={{ fill: "#f1f5f9" }} dataKey="value" cornerRadius={20} fill="#0f172a" />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.p className="text-4xl font-bold text-slate-900" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.3, type: "spring", stiffness: 120 }}>{analise.score_final.toFixed(1)}</motion.p>
                    <p className="text-xs text-slate-400 font-medium">/ 10.0</p>
                  </div>
                </div>
                <p className="text-sm text-slate-500 font-medium uppercase tracking-wider">Score Fundamentalista</p>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h3 className="text-sm font-bold text-slate-900 mb-4">Indicadores Chave</h3>
                <div className="grid grid-cols-2 gap-3">
                  <MiniCard titulo="P/L" valor={analise.indicadores["P/L"]} />
                  <MiniCard titulo="P/VP" valor={analise.indicadores["P/VP"]} />
                  <MiniCard titulo="ROE" valor={analise.indicadores["ROE"]} sufixo="%" />
                  <MiniCard titulo="Margem Líq." valor={analise.indicadores["Margem Líq."]} sufixo="%" />
                  <MiniCard titulo="Div. Yield" valor={analise.indicadores["Div. Yield"]} sufixo="%" />
                  <MiniCard titulo="Setor" valor={null} />
                </div>
              </div>
            </motion.div>

            <motion.div className="lg:col-span-2 space-y-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h3 className="text-lg font-bold text-slate-900 mb-6">🩺 Saúde da Empresa</h3>
                <BarraScore nome="Rentabilidade" detalhe={analise.detalhes.rentabilidade} index={1} />
                <BarraScore nome="Valuation" detalhe={analise.detalhes.valuation} index={2} />
                <BarraScore nome="Crescimento" detalhe={analise.detalhes.crescimento} index={3} />
                <BarraScore nome="Endividamento" detalhe={analise.detalhes.endividamento} index={4} />
                <BarraScore nome="Dividendos" detalhe={analise.detalhes.dividendos} index={5} />
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white text-sm">🤖</div>
                    <h3 className="text-lg font-bold text-slate-900">Diagnóstico IA</h3>
                  </div>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">92% Confiança</span>
                </div>
                
                <div className="prose prose-sm prose-slate max-w-none mb-6">
                  <ReactMarkdown components={{ p: ({node, ...props}) => <p className="text-slate-600 leading-relaxed mb-4" {...props} />, h3: ({node, ...props}) => <h3 className="text-slate-900 font-bold mt-4 mb-2" {...props} />, li: ({node, ...props}) => <li className="text-slate-600 ml-4 list-disc" {...props} />, strong: ({node, ...props}) => <strong className="font-bold text-slate-800" {...props} /> }}>{analise.relatorio_ia}</ReactMarkdown>
                </div>

                {/* ÁREA DE CHAT FUNCIONAL */}
                <div className="border-t border-slate-100 pt-4 mt-4">
                  <p className="text-xs text-slate-500 font-medium mb-2">Pergunte à IA sobre esta análise:</p>
                  
                  <div className="flex flex-wrap gap-2 mb-4">
                    <button onClick={() => enviarPergunta("Por que o crescimento está baixo?")} className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full transition-colors">Por que o crescimento está baixo?</button>
                    <button onClick={() => enviarPergunta("Explique o que é P/L")} className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full transition-colors">Explique o que é P/L</button>
                    <button onClick={() => enviarPergunta("Vale a pena comprar?")} className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full transition-colors">Vale a pena comprar?</button>
                  </div>

                  <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
                    {chatHistorico.map((msg, index) => (
                      <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        <div className={`max-w-[80%] p-3 rounded-xl text-sm ${msg.role === "user" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-800"}`}>
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                      </div>
                    ))}
                    {chatLoading && (
                      <div className="flex justify-start">
                        <div className="bg-slate-100 text-slate-400 p-3 rounded-xl text-sm">Digitando...</div>
                      </div>
                    )}
                  </div>

                  <form onSubmit={(e) => { e.preventDefault(); enviarPergunta(pergunta); }} className="relative">
                    <input type="text" value={pergunta} onChange={(e) => setPergunta(e.target.value)} placeholder="Faça sua pergunta..." className="w-full p-3 pr-10 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-900 focus:outline-none text-sm text-slate-900" />
                    <button type="submit" disabled={chatLoading} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-900 disabled:text-slate-300">➤</button>
                  </form>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </main>
  );
}