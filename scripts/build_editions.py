"""Build one canonical pagination for the web reader and its PDF download."""
import json,re,pathlib,html,unicodedata
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT=pathlib.Path('public/books')
CATALOG=json.loads(pathlib.Path('catalog.json').read_text(encoding='utf-8'))
for name,file in [('Book','georgia.ttf'),('BookBold','georgiab.ttf'),('BookItalic','georgiai.ttf'),('Label','calibri.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(pathlib.Path('C:/Windows/Fonts')/file)))
WIDTH,HEIGHT=350,510
CONTENT_WIDTH=290
CONTENT_HEIGHT=401
STYLES={
 'body':ParagraphStyle('body',fontName='Book',fontSize=12.5,leading=20,spaceAfter=10,textColor=HexColor('#283025')),
 'heading':ParagraphStyle('heading',fontName='BookBold',fontSize=18,leading=25,spaceAfter=20,textColor=HexColor('#283025')),
 'credits':ParagraphStyle('credits',fontName='Label',fontSize=10,leading=16,spaceAfter=10),
}
def norm(text):
 return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFD',text).encode('ascii','ignore').decode().lower())
def clean(text):
 return re.sub(r'[_#]','',text).strip()
def roman(text):
 match=re.fullmatch(r'[-.=\s]*([IVXLCDM]+)[-.=\s]*',text)
 return match.group(1) if match else None
def sections(book,ps):
 num=book['id'];out=[];part=1
 def add(i,title,group='',level=0):out.append(dict(paragraph=i,title=clean(title),group=group,level=level))
 if num in [2000,25956]:
  previous=False
  for i,p in enumerate(ps):
   if re.match(r'^Cap[ií]tulo\s+(?:[IVXLCDM]+\b|primero\b)',p,re.I) and len(p)<500:
    first=bool(re.match(r'^Cap[ií]tulo\s+(?:I\b|primero\b)',p,re.I))
    if first and previous:part+=1
    previous=True
    title=p
    if num==25956 and i+1<len(ps) and len(ps[i+1])<160:title+=' · '+ps[i+1]
    add(i,title,'Primera parte' if part==1 else 'Segunda parte')
 elif num in [17340,17223,49836,29506]:
  for i,p in enumerate(ps):
   r=roman(p)
   if r and (num!=29506 or 74<i<next((j for j,p in enumerate(ps) if p=="NOTES"),len(ps))):
    title='Capítulo '+r
    if num in [17340,17223,29506] and i+1<len(ps) and len(ps[i+1])<160:title+=' · '+ps[i+1]
    add(i,title)
   elif num==49836 and p in ['PRÓLOGO','POST-PRÓLOGO','ORACIÓN FÚNEBRE']:add(i,p.title())
  if num==29506:
   for i,p in enumerate(ps):
    if p in ['PREFACE','INTRODUCTION','PREFACIO DEL AUTOR','NOTES','VOCABULARY','FOOTNOTES']:add(i,p.title())
 elif num==13507:
  for i,p in enumerate(ps):
   if i>4 and p.startswith('#') and p.endswith('#') and p.isupper() and p!='#INDICE#':add(i,clean(p).title())
 elif num==50027:
  act=''
  for i,p in enumerate(ps):
   if re.fullmatch(r'ACTO (?:PRIMERO|SEGUNDO|TERCERO)\.',p):act=p.title();add(i,act)
   elif re.fullmatch(r'ESCENA [IVXLCDM]+\.',p) and act:add(i,p.title(),act,1)
 elif num==10814:
  names=['PREFACE','INTRODUCTION','BIBLIOGRAPHICAL NOTE','SPANISH PROSODY','DESDE MI CELDA','LOS OJOS VERDES','LA CORZA BLANCA','LA AJORCA DEL ORO','EL CRISTO DE LA CALAVERA','EL BESO','MAESE PÉREZ EL ORGANISTA','LA CRUZ DEL DIABLO','CREED EN DIOS','LAS HOJAS SECAS','RIMAS','VOCABULARY']
  for i,p in enumerate(ps):
   title=re.sub(r'\[\d+\]','',p)
   if title in names:add(i,title.title())
 elif num==15206:
  names=['EL ARTÍCULO DE FONDO','LA MULA Y EL BUEY','LA PLUMA EN EL VIENTO','LA CONJURACIÓN DE LAS PALABRAS','UN TRIBUNAL LITERARIO','LA PRINCESA Y EL GRANUJA']
  for i,p in enumerate(ps):
   if i==13:add(i,'Torquemada en la hoguera')
   elif p in names:add(i,p.title())
 elif num in [52894,19898]:
  source=pathlib.Path(f'scripts/source-cache/{num}.html').read_text(encoding='utf-8')
  titles=[]
  for title in re.findall(r'<h2\b[^>]*>(.*?)</h2>',source,re.S|re.I):
   text=html.unescape(re.sub('<[^>]+>',' ',title));text=re.sub(r'\s+',' ',text).strip()
   if text and not text.startswith('The Project Gutenberg'):titles.append(norm(text))
  start=8 if num==19898 else 11
  for i,p in enumerate(ps):
   if i>=start and 4<len(p)<150 and len(norm(clean(p)))>3 and (num!=52894 or i<next((j for j,t in enumerate(ps) if j>800 and t=="INDICE"),len(ps))) and any(t.startswith(norm(clean(p))) for t in titles) and norm(p) not in [norm(book['author'])]:add(i,p.title())
 out.sort(key=lambda x:x['paragraph'])
 seen=set();out=[x for x in out if not(x['paragraph'] in seen or seen.add(x['paragraph']))]
 return out

def flow(text,kind='body'):
 return Paragraph(html.escape(text),STYLES[kind])
def paginate(book,ps,ss):
 pages=[dict(type='cover',blocks=[]),dict(type='credits',blocks=[dict(kind='credits',text=f"{book['title']} · {book['author']}"),dict(kind='credits',text='Edición de lectura Margen. Texto íntegro de la edición digital de Project Gutenberg. Las portadas y la composición son propias de Margen; no son cubiertas comerciales.'),dict(kind='credits',text=f"Fuente y créditos: https://www.gutenberg.org/ebooks/{book['id']}"),dict(kind='credits',text='La ortografía y el contenido de las ediciones históricas se conservan. La numeración de esta edición digital es la misma en el lector y en el PDF. Créditos y licencia originales al final.')])]
 blocks=[];used=0;lookup={};by_para={s['paragraph']:s for s in ss}
 def flush():
  nonlocal blocks,used
  if blocks:pages.append(dict(type='text',blocks=blocks));blocks=[];used=0
 for i,p in enumerate(ps):
  text=clean(p)
  if not text:continue
  is_heading=i in by_para
  if is_heading:flush();by_para[i]['page']=len(pages)
  lookup[i]=len(pages)
  kind='heading' if is_heading else 'body'
  words=text.split();first=True
  while words:
   stylekind=kind if first else 'body'
   if used>CONTENT_HEIGHT-45:flush()
   avail=CONTENT_HEIGHT-used
   lo,hi=1,len(words);fit=0
   while lo<=hi:
    mid=(lo+hi)//2;segment=' '.join(words[:mid]);height=flow(segment,stylekind).wrap(CONTENT_WIDTH,avail)[1]+STYLES[stylekind].spaceAfter
    if height<=avail:fit=mid;lo=mid+1
    else:hi=mid-1
   if not fit:
    if blocks:flush();continue
    raise ValueError(f"A word cannot fit: {book['id']} {text[:100]}")
   segment=' '.join(words[:fit]);words=words[fit:]
   height=flow(segment,stylekind).wrap(CONTENT_WIDTH,avail)[1]+STYLES[stylekind].spaceAfter
   blocks.append(dict(kind=stylekind,text=segment));used+=height;first=False
   if words:flush()
 flush()
 return pages,lookup

def write_pdf(book,pages,chapters):
 filename=ROOT/f"{book['id']}.pdf";c=Canvas(str(filename),pagesize=(WIDTH,HEIGHT),pageCompression=1)
 c.setTitle(book['title']+' — Margen');c.setAuthor(book['author']);c.setSubject('Edición completa de lectura, fuente Project Gutenberg')
 links={x['page']:x for x in chapters}
 for i,page in enumerate(pages):
  c.setFillColor(HexColor('#fcf8eb'));c.rect(0,0,WIDTH,HEIGHT,stroke=0,fill=1)
  if page['type']=='cover':
   c.setFillColor(HexColor(book['colors'][1]));c.rect(0,0,WIDTH,HEIGHT,stroke=0,fill=1)
   c.setFillColor(HexColor(book['colors'][2]));c.setFont('Label',10);c.drawString(35,HEIGHT-45,'M A R G E N   /   B I B L I O T E C A')
   style=ParagraphStyle('cover',fontName='Book',fontSize=34,leading=41,textColor=HexColor(book['colors'][2]))
   title=Paragraph(html.escape(book['title']),style);_,ht=title.wrap(WIDTH-70,250);title.drawOn(c,35,HEIGHT-125-ht)
   c.setFont('BookItalic',14);c.drawString(35,90,book['author']);c.setFont('Label',9);c.drawString(35,48,'EDICIÓN COMPLETA · LECTURA LIBRE')
  else:
   c.setStrokeColor(HexColor('#d6d1bf'));c.line(30,HEIGHT-47,WIDTH-30,HEIGHT-47)
   c.setFillColor(HexColor('#777e6f'));c.setFont('Label',7);c.drawCentredString(WIDTH/2,HEIGHT-34,book['title'].upper())
   y=HEIGHT-67
   for block in page['blocks']:
    paragraph=flow(block['text'],block['kind']);_,ht=paragraph.wrap(CONTENT_WIDTH,HEIGHT)
    paragraph.drawOn(c,30,y-ht);y-=ht+STYLES[block['kind']].spaceAfter
   assert y>=30,(book['id'],i,y)
   c.setFillColor(HexColor('#777e6f'));c.setFont('Book',9);c.drawCentredString(WIDTH/2,19,str(i+1))
  if i in links:
   key='page-'+str(i);c.bookmarkPage(key);c.addOutlineEntry(links[i]['title'][:180],key,level=0,closed=False)
  c.showPage()
 c.save()

def build(book):
 path=ROOT/f"{book['id']}.json";data=json.loads(path.read_text(encoding='utf-8'));ps=data['paragraphs'];ss=sections(book,ps)
 pages,lookup=paginate(book,ps,ss)
 # The original license is redistributed inside both reading formats.
 raw=(pathlib.Path('scripts/source-cache')/f"{book['id']}-original.txt").read_text(encoding='utf-8')
 epilogue=re.split(r'\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n',raw,maxsplit=1)
 if len(epilogue)>1:
  license_ps=['Créditos y licencia de la edición original']+[re.sub(r'\s+',' ',p).strip() for p in re.split(r'\n\s*\n',epilogue[1]) if p.strip()]
  lp,_=paginate(book,license_ps,[]);license_page=len(pages);pages+=lp[2:];ss.append(dict(title='Créditos y licencia',group='',level=0,paragraph=len(ps),page=license_page))
 expected=' '.join(' '.join(clean(p).split()) for p in ps if clean(p))
 actual=' '.join(b['text'] for p in pages[2:len(pages)-(len(lp)-2) if len(epilogue)>1 else len(pages)] for b in p['blocks'])
 assert actual==expected,f"Text changed in {book['id']}"
 assert all(ss[i]['page']<ss[i+1]['page'] for i in range(len(ss)-1)),f"Unordered chapters: {book['id']}"
 if book['id']==2000:assert len([x for x in ss if x['title'].startswith('Capítulo')])==126
 if book['id']==17340:assert len(ss)==23
 if book['id']==13507:assert len(ss)==19
 write_pdf(book,pages,ss)
 data.update(version=3,pages=pages,chapters=ss,paragraphPages=lookup)
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8',newline='\n')
 book['pages']=len(pages)
 print(book['id'],len(pages),'pages',len(ss),'sections',flush=True)

if __name__=='__main__':
 for book in CATALOG:build(book)
 pathlib.Path('catalog.json').write_text(json.dumps(CATALOG,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')


