import re
import urllib.request
from urllib.parse import quote
import json

def to_synthetic_email(uname: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\.]', '', uname.strip().lower())
    return f"{cleaned}@pea.local"

def resolve_sector(isin, name):
    name_u = str(name).upper()
    if 'ETF' in name_u or 'STOXX' in name_u or 'MSCI' in name_u or 'AMUNDI' in name_u:
        return 'ETF & Indice'
    if 'LVMH' in name_u or 'HERMES' in name_u or 'KERING' in name_u or 'L\'OREAL' in name_u:
        return 'Luxe'
    if 'TOTAL' in name_u or 'ENERGY' in name_u:
        return 'Énergie'
    if 'APPLE' in name_u or 'MICROSOFT' in name_u or 'TECH' in name_u:
        return 'Technologie'
    return 'Action'

def search_yf_symbol_online(query):
    if not query: return None
    try:
        q_clean = quote(str(query).strip())
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q_clean}&newsCount=0"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            quotes = data.get('quotes', [])
            if not quotes: return None
            for q in quotes:
                sym = q.get('symbol', '')
                if sym.endswith('.PA'): return sym
            for q in quotes:
                sym = q.get('symbol', '')
                if sym and not sym.startswith('^'): return sym
    except Exception:
        pass
    return None

def resolve_yf_symbol(isin, name):
    isin_clean = str(isin).strip().upper() if isin else ""
    if isin_clean == 'FR0000121014': return 'MC.PA'
    if isin_clean == 'FR0000120271': return 'TTE.PA'
    if isin_clean == 'US0378331005': return 'AAPL'
    if isin_clean == 'US5949181045': return 'MSFT'
    if isin_clean == 'LU1681043599': return 'CW8.PA'
    if isin_clean == 'FR0000075954': return 'ALRIB.PA'
    if isin_clean == 'FR0000131104': return 'BNP.PA'
    if isin_clean == 'FR0011726835': return 'GTT.PA'
    if isin_clean == 'FR0000121972': return 'SU.PA'
    if isin_clean == 'FR0014007ND6': return 'ALHAF.PA'
    if isin_clean == 'FR0013341781': return 'AL2SI.PA'
    if isin_clean == 'FR0011550193': return 'ETZ.PA'
    if isin_clean == 'FR0000133308': return 'ORA.PA'
    if isin_clean == 'FR0000073272': return 'SAF.PA'
    if isin_clean == 'FR0014018PW8': return 'ALDAT.PA'
    if isin_clean == 'FR0011049824': return 'ALMDT.PA'
    if isin_clean == 'FR0011341205': return 'NANO.PA'

    if isin_clean and len(isin_clean) >= 9:
        online = search_yf_symbol_online(isin_clean)
        if online: return online
        
    if name:
        online = search_yf_symbol_online(name)
        if online: return online
        
    if isin_clean.startswith('FR'): return str(name).split()[0] + '.PA'
    if isin_clean.startswith('US'): return str(name).split()[0]
    return name
