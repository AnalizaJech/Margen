import json,re,pathlib
for num in [2000,17340,25956,10814]:
 d=json.loads(pathlib.Path(f'public/books/{num}.json').read_text(encoding='utf-8'))
 print('\nBOOK',num)
 for i,p in enumerate(d['paragraphs']):
  if len(p)<150 and (re.match(r'^(?:Cap[ií]tulo|CAP[IÍ]TULO|[-—]?[IVXLCDM]+[-—.]?$|[IVXLCDM]+\.)',p) or p.isupper()):
   print(i,repr(p[:140]))
