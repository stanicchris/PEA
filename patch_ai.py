import re

with open('ai_advisor.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('import streamlit as st\n', '')

new_func = '''def get_groq_api_key():
    import os
    return os.environ.get("GROQ_API_KEY", "")'''

content = re.sub(r'def get_groq_api_key\(\):.*?return os\.environ\.get\("GROQ_API_KEY", ""\)', new_func, content, flags=re.DOTALL)

with open('ai_advisor.py', 'w', encoding='utf-8') as f:
    f.write(content)
