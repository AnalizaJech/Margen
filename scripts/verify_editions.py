import pathlib,json,pymupdf
catalog=json.loads(pathlib.Path('catalog.json').read_text(encoding='utf-8'))
for book in catalog:
 data=json.loads(pathlib.Path(f"public/books/{book['id']}.json").read_text(encoding='utf-8'));pdf=pymupdf.open(f"public/books/{book['id']}.pdf")
 assert len(pdf)==len(data['pages'])==book['pages']
 assert all(a['page']<b['page'] for a,b in zip(data['chapters'],data['chapters'][1:]))
 assert all(c['title'].strip() and len(''.join(x for x in c['title'] if x.isalnum()))>0 for c in data['chapters'])
 assert len(pdf.get_toc())==len(data['chapters'])
 for c in data['chapters']:assert c['page']<len(pdf)
print('12 complete editions: PDF counts, outlines and chapter order passed')
