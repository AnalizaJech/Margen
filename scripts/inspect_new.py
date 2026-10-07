import json,pathlib,re
for num in [13507,17223,52894,19898,50027,49836,15206,29506]:
 ps=json.loads(pathlib.Path(f'public/books/{num}.json').read_text(encoding='utf-8'))['paragraphs']
 print('\n',num,'FIRST',[(i,p[:100]) for i,p in enumerate(ps[:20])]);print('SHORT',[(i,p[:100]) for i,p in enumerate(ps) if len(p)<100 and (re.match(r'^[#=-]*[IVXLCDM]+[.= -]*$',p) or p.isupper())][:50])
