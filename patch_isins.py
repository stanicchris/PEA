content = open('backend/main.py', encoding='utf-8').read()
mapping = """
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
"""
content = content.replace("if isin_clean == 'LU1681043599': return 'CW8.PA'", "if isin_clean == 'LU1681043599': return 'CW8.PA'" + mapping)
with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
