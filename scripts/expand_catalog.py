import json,pathlib,re,urllib.request,concurrent.futures,html
root=pathlib.Path('public/books');cache=pathlib.Path('scripts/source-cache');cache.mkdir(exist_ok=True)
data=json.loads(pathlib.Path('catalog.json').read_text(encoding='utf-8-sig'))
extra=[
(13507,'Cuentos de amor, de locura y de muerte','Horacio Quiroga','Cuentos',1917,'viaje','Relatos donde el amor, la naturaleza y el peligro se encuentran. Historias intensas para leer una a una.'),
(17223,'Pepita Jiménez','Juan Valera','Narrativa',1874,'calma','Una novela sobre el deseo y la vocación, contada a través de cartas y del encuentro con una joven viuda andaluza.'),
(52894,'Azul…','Rubén Darío','Poesía',1888,'calma','Cuentos y poemas donde la música del lenguaje y la imaginación abren las puertas al modernismo.'),
(19898,'La Edad de Oro','José Martí','Cuentos',1889,'ideas','Historias, poemas y descubrimientos para los niños de América. Los cuatro números de la publicación reunidos en una edición.'),
(50027,'El sí de las niñas','Leandro Fernández de Moratín','Teatro',1806,'ideas','Una comedia en tres actos sobre la libertad de elegir, los afectos y las expectativas familiares.'),
(49836,'Niebla','Miguel de Unamuno','Narrativa',1914,'ideas','Augusto Pérez busca sentido entre el amor y la incertidumbre, en una novela que cuestiona sus propios límites.'),
(15206,'Torquemada en la hoguera','Benito Pérez Galdós','Narrativa',1889,'ideas','Un prestamista se enfrenta a una crisis que sacude sus certezas. Esta edición incluye otros relatos de Galdós.'),
(29506,'El sombrero de tres picos','Pedro Antonio de Alarcón','Clásicos',1874,'viaje','Un molino, una pareja y un corregidor dan forma a una comedia de enredos, sospechas e identidades cambiadas. Edición anotada.')]
colors=[['#e7dfd5','#995f40','#f6ecd6','#dca974'],['#e0e6dd','#556b50','#f2e9d0','#c6ac7a'],['#dce3e7','#34596d','#f3e7d0','#e1b465'],['#e9e4d1','#ba9c41','#303c30','#efdd97'],['#e7dce0','#7d4154','#f7e9d9','#d99494'],['#e0e3dc','#546463','#efe9dc','#ad9f83']]
for i,b in enumerate(extra):
 if not any(x['id']==b[0] for x in data):data.append(dict(id=b[0],title=b[1],author=b[2],category=b[3],year=b[4],mood=b[5],description=b[6],language='Español',colors=colors[i%len(colors)],tag='Texto completo · Español',prompt='¿Qué idea de esta lectura se queda contigo?',pages=0))
data[-1]['language']='Español / inglés';data[-1]['tag']='Edición anotada · ES / EN'
pathlib.Path('catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def download(b):
 num=b['id'];original=cache/f'{num}-original.txt'
 if not original.exists():
  raw=urllib.request.urlopen(f'https://www.gutenberg.org/cache/epub/{num}/pg{num}.txt',timeout=60).read().decode('utf-8-sig').replace('\r','');original.write_text(raw,encoding='utf-8',newline='\n')
 else:raw=original.read_bytes().decode('utf-8-sig').replace('\r','');original.write_text(raw,encoding='utf-8',newline='\n')
 body=re.split(r'\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n',raw,maxsplit=1)[-1]
 body=re.split(r'\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK',body,maxsplit=1)[0]
 paragraphs=[re.sub(r'\s*\n\s*',' ',p).strip() for p in re.split(r'\n\s*\n',body)]
 paragraphs=[p for p in paragraphs if p]
 (root/f'{num}.json').write_text(json.dumps({'source':f'https://www.gutenberg.org/ebooks/{num}','paragraphs':paragraphs},ensure_ascii=False),encoding='utf-8')
 source=cache/f'{num}.html'
 if not source.exists():source.write_bytes(urllib.request.urlopen(f'https://www.gutenberg.org/cache/epub/{num}/pg{num}-images.html',timeout=60).read())
 headings=re.findall(r'<h([1-4])\b[^>]*>(.*?)</h\1>',source.read_text(encoding='utf-8'),re.S|re.I)
 print(num,len(paragraphs),'HEADINGS',[(x,html.unescape(re.sub('<[^>]+>',' ',t)).strip()[:110]) for x,t in headings[:12]],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,data))
