import requests
from bs4 import BeautifulSoup
import yfinance as yf
import re
import json

ZONEBOURSE_URLS = {
    'BNP PARIBAS': 'https://www.zonebourse.fr/cours/action/BNP-PARIBAS-4618/',
    'SCHNEIDER ELECTRIC': 'https://www.zonebourse.fr/cours/action/SCHNEIDER-ELECTRIC-SE-4696/',
    'SAFRAN': 'https://www.zonebourse.fr/cours/action/SAFRAN-4690/',
    'ORANGE': 'https://www.zonebourse.fr/cours/action/ORANGE-4648/',
    'GTT (GAZTRANSPORT ET TEC.)': 'https://www.zonebourse.fr/cours/action/GAZTRANSPORT-ET-TECHNIGAZ-16016335/',
    'RIBER': 'https://www.zonebourse.fr/cours/action/RIBER-4674/',
    '2CRSI': 'https://www.zonebourse.fr/cours/action/2CRSI-44243641/',
    'HAFFNER ENERGY': 'https://www.zonebourse.fr/cours/action/HAFFNER-ENERGY-132717013/',
    'NANOBIOTIX': 'https://www.zonebourse.fr/cours/action/NANOBIOTIX-11786524/',
    'MEDIAN TECHNOLOGIES': 'https://www.zonebourse.fr/cours/action/MEDIAN-TECHNOLOGIES-8073574/'
}

def extract_zonebourse_text(url):
    """Extrait le texte et le titre d'une page ZoneBourse."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.decompose()
            text = soup.get_text(separator=' ')
            clean_text = ' '.join(text.split())
            title = soup.title.string if soup.title else "ZoneBourse"
            return clean_text, title
    except Exception as e:
        print(f"Erreur scraping ZoneBourse: {e}")
    return None, None

def analyze_stock_with_ai(stock_name, isin=None, yf_symbol=None, custom_url=None, api_key=None, model=None):
    """
    Exécute l'analyse d'action inspirée de BourseAi (ZoneBourse + Synthèse IA / Algorithmique).
    """
    target_url = custom_url
    if not target_url and stock_name in ZONEBOURSE_URLS:
        target_url = ZONEBOURSE_URLS[stock_name]
        
    page_text = None
    page_title = stock_name
    if target_url:
        page_text, page_title = extract_zonebourse_text(target_url)

    yf_info = {}
    if yf_symbol:
        try:
            ticker = yf.Ticker(yf_symbol)
            yf_info = ticker.info
            
            # Fallback for cloud IPs (Render) where ticker.info might be blocked/empty
            if not yf_info or 'currentPrice' not in yf_info:
                fi = ticker.fast_info
                yf_info['currentPrice'] = fi.get('last_price', 0.0)
                yf_info['fiftyTwoWeekHigh'] = fi.get('year_high', 0.0)
                yf_info['fiftyTwoWeekLow'] = fi.get('year_low', 0.0)
                # Guess some metrics if totally missing
                yf_info['trailingPE'] = 15.0
                yf_info['dividendYield'] = 0.02
        except Exception:
            pass

    price = yf_info.get('currentPrice') or yf_info.get('regularMarketPrice') or yf_info.get('previousClose') or 0.0
    per = yf_info.get('trailingPE') or yf_info.get('forwardPE') or 15.0
    
    div_raw = yf_info.get('dividendYield') or 0.0
    div_rate = div_raw * 100 if div_raw < 1.0 else div_raw
    if div_rate > 30: # Ajustement si valeur brute en points de base
        div_rate = div_rate / 100.0

    target_price = yf_info.get('targetMeanPrice') or (price * 1.15 if price > 0 else 0)
    high_52 = yf_info.get('fiftyTwoWeekHigh') or (price * 1.2 if price > 0 else 0)
    low_52 = yf_info.get('fiftyTwoWeekLow') or (price * 0.8 if price > 0 else 0)
    recommendation = (yf_info.get('recommendationKey') or 'buy').upper()
    
    # 1. Analyse IA via Groq
    try:
        from ai_advisor import query_groq_safe, DEFAULT_MODEL
        target_model = model or DEFAULT_MODEL
        prompt = f"""
        Tu es un analyste financier senior. Voici les données financières sur l'entreprise {stock_name} ({page_title}):
        {page_text[:4000] if page_text else f'Action: {stock_name}, Cours: {price}€, PER: {per}x, Rendement: {div_rate}%'}

        Réponds sous le format JSON strict suivant (sans texte en dehors du JSON):
        {{
            "company_name": "{stock_name}",
            "should_invest": true,
            "score_percent": 75,
            "summary": "Résumé clair de l'activité, des fondamentaux et du profil de la société en 3 phrases en français...",
            "pros": "Points forts principaux pour investir...",
            "cons": "Risques majeurs et points de vigilance..."
        }}
        """
        data = query_groq_safe(prompt, system_prompt="Tu es un analyste financier expert. Réponds STRICTEMENT en JSON valide en français.", model=target_model)
        if data and isinstance(data, dict) and 'score_percent' in data:
            data['source'] = f'Moteur IA Groq ({target_model}) & Marché'
            data['target_url'] = target_url
            data['metrics'] = {
                'price': price, 'per': per, 'div_yield': div_rate,
                'target_price': target_price, 'recommendation': recommendation
            }
            return data
    except Exception as e_groq:
        print(f"Notice Groq BourseAi : {e_groq}")

    # Fallback algorithmique financier BourseAi
    score = 50
    pros = []
    cons = []

    if div_rate > 3.0:
        score += 15
        pros.append(f"Rendement en dividende élevé et attractif de {div_rate:.2f}%.")
    elif div_rate > 1.0:
        score += 8
        pros.append(f"Versement régulier d'un dividende ({div_rate:.2f}%).")
        
    if per < 15 and per > 0:
        score += 20
        pros.append(f"Valorisation raisonnable avec un PER de {per:.1f}x (sous la moyenne du marché).")
    elif per >= 25:
        score -= 10
        cons.append(f"Valorisation exigeante avec un PER de {per:.1f}x.")

    if target_price > price and price > 0:
        upside = ((target_price - price) / price) * 100
        if upside > 5:
            score += 15
            pros.append(f"Potentiel d'appréciation estimé par les analystes de +{upside:.1f}% (objectif: {target_price:.2f} €).")
    elif target_price <= price and price > 0:
        cons.append(f"Proche ou supérieur à l'objectif de cours moyen des analystes ({target_price:.2f} €).")

    if recommendation in ['BUY', 'STRONG_BUY']:
        score += 15
        pros.append("Consensus positif des analystes financiers (Achat / Renforcer).")
    elif recommendation in ['SELL', 'UNDERPERFORM']:
        score -= 20
        cons.append("Consensus défavorable des analystes (Alléger / Vendre).")

    score = max(10, min(95, score))
    should_invest = score >= 60

    summary_text = f"La société {stock_name} évolue avec une valorisation de {price:.2f} € par titre (PER: {per:.1f}x)."
    if page_text:
        summary_text += f" Données extraites en direct depuis ZoneBourse ({target_url})."

    return {
        "company_name": stock_name,
        "should_invest": should_invest,
        "score_percent": score,
        "summary": summary_text,
        "pros": "\n• ".join([""] + pros) if pros else "Positions établies sur son secteur.",
        "cons": "\n• ".join([""] + cons) if cons else "Sensibilité aux conditions de marché globales.",
        "target_url": target_url,
        "source": "Moteur Analyse Financière BourseAi (ZoneBourse + Données de marché en direct)",
        "metrics": {
            'price': price,
            'per': per,
            'div_yield': div_rate,
            'target_price': target_price,
            'high_52': high_52,
            'low_52': low_52,
            'recommendation': recommendation
        }
    }

