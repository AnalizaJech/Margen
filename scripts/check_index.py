import json,pathlib
for num in [52894,19898,29506]:
 d=json.loads(pathlib.Path(f'public/books/{num}.json').read_text(encoding='utf-8'))
 print('\n',num)
 for ch in d['chapters']:print(ch['paragraph'],ch['page']+1,ch['title'][:100])
