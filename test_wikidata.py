import requests
url = 'https://query.wikidata.org/sparql'
query = 'SELECT ?ticker WHERE { ?item wdt:P2376 "FR0000121014". ?item wdt:P249 ?ticker. }'
res = requests.get(url, params={'query': query, 'format': 'json'}, headers={'User-Agent': 'Mozilla/5.0'})
print(res.status_code, res.json())
