import json

class AgenteAvaliador:
    def __init__(self):
        # Pesos das categorias definidos no PRD
        self.pesos = {
            "rentabilidade": 0.30,
            "valuation": 0.25,
            "crescimento": 0.20,
            "endividamento": 0.15,
            "dividendos": 0.10
        }

    def _avaliar_indicador(self, valor, regras, menor_eh_melhor=False):
        """Método auxiliar para aplicar as regras e dar a nota de 0 a 10"""
        if valor is None:
            return None, "Sem dados"
        
        if menor_eh_melhor:
            # Indicadores como P/L, P/VP, Dívida: avaliamos do menor limite para o maior
            for limite, nota, classificacao in sorted(regras):
                if valor <= limite:
                    return nota, classificacao
        else:
            # Indicadores como ROE, Margem: avaliamos do maior limite para o menor
            for limite, nota, classificacao in sorted(regras, reverse=True):
                if valor >= limite:
                    return nota, classificacao
        
        # Se não cair em nenhuma regra positiva, recebe a nota mínima
        return 0, "Crítico"

    def avaliar(self, dados: dict) -> dict:
        print(f"⚖️ Agente 3: Avaliando indicadores de {dados.get('ticker')}...")
        
        # 1. Rentabilidade
        roe_nota, roe_class = self._avaliar_indicador(dados.get("roe"), [(20, 10, "Excelente"), (15, 8, "Muito Bom"), (10, 6, "Bom"), (5, 4, "Aceitável"), (0, 2, "Ruim")])
        margem_nota, margem_class = self._avaliar_indicador(dados.get("margem_liquida"), [(20, 10, "Excelente"), (15, 8, "Muito Boa"), (10, 6, "Boa"), (5, 4, "Razoável"), (0, 2, "Baixa")])
        
        notas_rent = [n for n in [roe_nota, margem_nota] if n is not None]
        media_rent = sum(notas_rent) / len(notas_rent) if notas_rent else 0

        # 2. Valuation (Menor é melhor)
        pl_nota, pl_class = self._avaliar_indicador(dados.get("pl"), [(10, 10, "Muito Barato"), (15, 8, "Atrativo"), (20, 6, "Razoável"), (30, 4, "Caro"), (9999, 2, "Muito Caro")], menor_eh_melhor=True)
        pvp_nota, pvp_class = self._avaliar_indicador(dados.get("pvp"), [(1.0, 10, "Desconto"), (1.5, 8, "Barato"), (3.0, 6, "Justo"), (5.0, 4, "Caro"), (9999, 2, "Muito Caro")], menor_eh_melhor=True)
        
        notas_val = [n for n in [pl_nota, pvp_nota] if n is not None]
        media_val = sum(notas_val) / len(notas_val) if notas_val else 0

        # 3. Crescimento
        cresc_rec_nota, cresc_rec_class = self._avaliar_indicador(dados.get("crescimento_receita_5a"), [(15, 10, "Excelente"), (10, 8, "Forte"), (5, 6, "Moderado"), (0, 4, "Lento"), (-9999, 2, "Recolhendo")])
        cresc_luc_nota, cresc_luc_class = self._avaliar_indicador(dados.get("crescimento_lucro_5a"), [(20, 10, "Excelente"), (10, 8, "Forte"), (5, 6, "Moderado"), (0, 4, "Lento"), (-9999, 2, "Recolhendo")])
        
        notas_cresc = [n for n in [cresc_rec_nota, cresc_luc_nota] if n is not None]
        media_cresc = sum(notas_cresc) / len(notas_cresc) if notas_cresc else 0

        # 4. Endividamento (Menor é melhor - Yahoo usa Debt/Equity, adaptamos a regra)
        # Ex: 83.26 no Yahoo significa 0.83 de ratio. Consideramos < 1.0 ótimo.
        divida_nota, divida_class = self._avaliar_indicador(dados.get("divida_liquida_ebitda"), [(50, 10, "Excelente"), (100, 8, "Saudável"), (200, 6, "Moderado"), (300, 4, "Atenção"), (9999, 2, "Crítico")], menor_eh_melhor=True)

        notas_end = [n for n in [divida_nota] if n is not None]
        media_end = sum(notas_end) / len(notas_end) if notas_end else 0

        # 5. Dividendos
        dy_nota, dy_class = self._avaliar_indicador(dados.get("dividend_yield"), [(8, 10, "Excelente"), (6, 8, "Muito Bom"), (4, 6, "Bom"), (2, 4, "Baixo"), (0, 2, "Muito Baixo")])
        
        notas_div = [n for n in [dy_nota] if n is not None]
        media_div = sum(notas_div) / len(notas_div) if notas_div else 0

        # Cálculo do Score Final Ponderado
        score_final = (
            (media_rent * self.pesos["rentabilidade"]) +
            (media_val * self.pesos["valuation"]) +
            (media_cresc * self.pesos["crescimento"]) +
            (media_end * self.pesos["endividamento"]) +
            (media_div * self.pesos["dividendos"])
        )

        resultado = {
            "ticker": dados.get("ticker"),
            "nome": dados.get("nome"),
            "score_final": round(score_final, 2),
            "detalhes": {
                "rentabilidade": {"nota": round(media_rent, 1), "classificacao": roe_class if roe_class else "N/A"},
                "valuation": {"nota": round(media_val, 1), "classificacao": pl_class if pl_class else "N/A"},
                "crescimento": {"nota": round(media_cresc, 1), "classificacao": cresc_rec_class if cresc_rec_class else "N/A"},
                "endividamento": {"nota": round(media_end, 1), "classificacao": divida_class if divida_class else "N/A"},
                "dividendos": {"nota": round(media_div, 1), "classificacao": dy_class if dy_class else "N/A"}
            },
            "dados_brutos": dados # Mantemos os dados brutos para a IA citar os números exatos
        }
        
        print(f"✅ Agente 3: Avaliação concluída. Score: {score_final:.2f}")
        return resultado

# Bloco de teste integrado com o Agente 1
if __name__ == "__main__":
    from agent1_coletor import AgenteColetor
    
    coletor = AgenteColetor()
    avaliador = AgenteAvaliador()
    
    ticker_teste = "PETR4"
    dados_brutos = coletor.buscar_dados(ticker_teste)
    
    if dados_brutos:
        resultado_final = avaliador.avaliar(dados_brutos)
        print("\n--- Resultado do Agente 3 (Pronto para a IA) ---")
        print(json.dumps(resultado_final, indent=4, ensure_ascii=False))