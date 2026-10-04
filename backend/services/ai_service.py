import os
import json
from groq import Groq
import pandas as pd

# Initialiser le client Groq
# Assurez-vous que GROQ_API_KEY est dans l'environnement
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

def generate_financial_advice(df: pd.DataFrame, cash: float, user_messages: list):
    """
    Appelle Groq avec Llama-3 pour agir comme conseiller financier.
    Prend en entrée l'historique des messages et injecte le contexte du portefeuille
    dans le prompt système.
    """
    
    if not os.environ.get("GROQ_API_KEY"):
        return {"error": "Clé API Groq non configurée."}
        
    portfolio_context = "Portefeuille vide."
    total_val = cash
    
    if not df.empty:
        # REMOVE this crashing line:
        # total_val += float((df['quantity'] * df['current_price']).sum())
        
        # Résumer les positions pour l'IA
        summary_positions = []
        for _, row in df.iterrows():
            # Safely handle missing columns or None values
            qty = float(row.get('quantity') or 0)
            c_price = float(row.get('last_price') or 0)
            pos_val = qty * c_price
            
            # Accumulate the total value safely:
            total_val += pos_val 
            
            pru = float(row.get('buying_price') or 0)
            perf = 0
            if pru > 0:
                perf = ((c_price - pru) / pru) * 100
                
            summary_positions.append({
                "ticker": row.get('isin'),
                "nom": row.get('name'),
                "valeur_actuelle_eur": round(pos_val, 2),
                "performance_pct": round(perf, 2),
                "secteur": row.get('sector', 'Inconnu')
            })
            
        # Trier par poids (valeur)
        summary_positions.sort(key=lambda x: x['valeur_actuelle_eur'], reverse=True)
        
        portfolio_context = f"""
Valorisation Totale Estimée (dont liquidités): {round(total_val, 2)} EUR
Liquidités (Cash): {round(cash, 2)} EUR
Top Lignes:
{json.dumps(summary_positions[:10], indent=2, ensure_ascii=False)}
        """

    system_prompt = f"""Tu es 'BourseAi', le conseiller financier virtuel exclusif de Capfolio. 
Tu es expert en investissement en bourse, particulièrement sur le Plan d'Épargne en Actions (PEA) français, l'investissement passif (ETF), le stock-picking de qualité, et la stratégie dividendes.
Ton ton est professionnel, concis, direct et encourageant. Tu utilises le tutoiement professionnel ou le vouvoiement, mais reste cohérent (préfère le vouvoiement poli).
Tu dois utiliser le contexte du portefeuille de l'utilisateur pour personnaliser tes réponses.

CONTEXTE DU PORTEFEUILLE DE L'UTILISATEUR:
{portfolio_context}

RÈGLES IMPORTANTES:
1. Ne donne pas de conseils financiers garantis (ajoute un petit disclaimer si tu recommandes d'acheter ou de vendre).
2. Fais des réponses courtes et percutantes, formattées en Markdown (utilise le gras, des listes à puces).
3. Si on te pose une question générale, réponds avec expertise. Si on te demande d'analyser le portefeuille, base-toi uniquement sur le CONTEXTE ci-dessus.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Ajouter les messages de l'utilisateur
    for msg in user_messages:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    try:
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return {"error": str(e)}
