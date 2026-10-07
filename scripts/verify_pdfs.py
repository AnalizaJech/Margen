import pathlib,json,pymupdf
out=pathlib.Path('tmp/pdfs');out.mkdir(parents=True,exist_ok=True)
for num in [17340,2000,13507,52894]:
 d=json.loads(pathlib.Path(f'public/books/{num}.json').read_text(encoding='utf-8'))
 pdf=pymupdf.open(f'public/books/{num}.pdf')
 assert len(pdf)==len(d['pages'])
 for index in [0,1,d['chapters'][0]['page'],len(pdf)//2,len(pdf)-1]:
  p=pdf[index]
  for block in p.get_text('blocks'):
   assert block[0]>=0 and block[1]>=0 and block[2]<=p.rect.width+1 and block[3]<=p.rect.height+1,(num,index,block[:4])
  p.get_pixmap(matrix=pymupdf.Matrix(1.8,1.8)).save(out/f'{num}-{index+1}.png')
 print(num,len(pdf),'PDF pages, QA passed')
