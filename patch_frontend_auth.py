import glob
import re

# 1. LoginWidget.vue
with open('src/components/LoginWidget.vue', 'r', encoding='utf-8') as f:
    lw = f.read()
lw = lw.replace("emit('login-success', { userId: data.user_id, username: data.username });",
                "localStorage.setItem('pea_access_token', data.access_token);\n        emit('login-success', { userId: data.user_id, username: data.username });")
with open('src/components/LoginWidget.vue', 'w', encoding='utf-8') as f:
    f.write(lw)

# 2. App.vue and others: add Authorization header
files = glob.glob('src/**/*.vue', recursive=True)
for filepath in files:
    if 'LoginWidget.vue' in filepath: continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # App.vue has `fetch(URL)` and `fetch(URL, { method: 'POST' })`
    # Replace simple fetch(URL) with fetch(URL, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } })
    content = re.sub(r'fetch\((`.+?`)\)', r"fetch(\1, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } })", content)
    
    # Replace fetch(URL, { ... }) to inject headers
    # Find fetch(..., { 
    # This is tricky with regex, we can just find `{ method: 'POST'` and add headers
    content = content.replace("{ method: 'POST' }", "{ method: 'POST', headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } }")
    
    # SettingsModal.vue has upload logic with FormData
    content = content.replace("body: formData", "headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') }, body: formData")
    
    # Also in SettingsModal: body: JSON.stringify({ user_id: props.userId, cash: newCash.value })
    content = content.replace("body: JSON.stringify({ user_id: props.userId, cash: newCash.value })", "body: JSON.stringify({ cash: newCash.value }), headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') }")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
