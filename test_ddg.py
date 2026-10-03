import requests, re, urllib.parse
from bs4 import BeautifulSoup
def search_ddg_ticker(query):
    try:
        res = requests.get(f'https://lite.duckduckgo.com/lite/', data={'q': f'{query} yahoo finance quote'}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'yahoo.com/quote/' in href:
                m = re.search(r'quote/([^/]+)', href)
                if m:
                    return m.group(1).upper()
            if 'uddg=' in href:
                url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                m = re.search(r'finance\.yahoo\.com/quote/([^/]+)', url)
                if m:
                    return m.group(1).upper()
    except Exception as e:
        print(e)
    return None
print('ISIN FR0013341781:', search_ddg_ticker('FR0013341781'))
print('LVMH:', search_ddg_ticker('LVMH'))
