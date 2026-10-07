import pathlib,re
p=pathlib.Path('app.js'); s=p.read_text(encoding='utf-8-sig'); start=s.index('const books = ['); end=s.index('const $ =')
books=[(2000,'Don Quijote de la Mancha','Miguel de Cervantes','Clásicos',1605,'viaje','La edición reúne las dos partes de las aventuras de don Quijote y Sancho Panza. Un viaje entre la imaginación, el humor y la realidad.','Español'),(17340,'Marianela','Benito Pérez Galdós','Narrativa',1878,'calma','La historia de Nela, una joven que guía a Pablo por el paisaje de las minas de Socartes. Una novela sobre el afecto, las apariencias y la desigualdad.','Español'),(25956,'La desheredada','Benito Pérez Galdós','Narrativa',1881,'ideas','Isidora llega a Madrid convencida de pertenecer a una familia aristocrática. Galdós retrata una ciudad donde las aspiraciones y la realidad chocan.','Español'),(10814,'Leyendas, cuentos y poemas','Gustavo Adolfo Bécquer','Poesía',1907,'viaje','Antología publicada en 1907, editada por Everett Ward Olmsted. Obras en español, introducción y notas en inglés. Se conserva esta edición íntegra.','Español / inglés')]
import json
colors=[['#e9e5d4','#b48338','#f3ead1','#93432e'],['#e5e8df','#174b48','#f1e8ce','#ef9a71'],['#e8dfdc','#8d443a','#f4e7ce','#e5b899'],['#dedfe4','#293b50','#f0dfbe','#dbaa57']]
data=[dict(id=b[0],title=b[1],author=b[2],category=b[3],pages=0,year=b[4],mood=b[5],description=b[6],language=b[7],colors=colors[i],tag='Texto completo · '+b[7],prompt='¿Qué idea de esta lectura se queda contigo?') for i,b in enumerate(books)]
s=s[:start]+'const books = '+json.dumps(data,ensure_ascii=False)+';\nwindow.margenBooks=books;\n'+s[end:]
s=s.replace('<span>Selección Margen ↗</span><span>${b.pages} páginas</span>','<span>Leer en flipbook ↗</span><span>Edición digital</span>')
s=s.replace('<span>${b.pages} páginas</span>','<span>${b.language}</span>')
s=s.replace('<button class="button dark" data-save="${id}">','<button class="button dark" data-read="${id}">Abrir libro ↗</button><p class="edition-source"><a href="https://www.gutenberg.org/ebooks/${id}" target="_blank" rel="noopener">Edición y créditos ↗</a></p><button class="text-button" data-save="${id}">')
s=s.replace('if(t.dataset.open)showBook',"if(t.dataset.read){t.closest('dialog').close();window.dispatchEvent(new CustomEvent('margen-read',{detail:Number(t.dataset.read)}))}if(t.dataset.open)showBook")
s=s.replace("if($('#sort').value","if(window.margenSort")
s=s.replace("$('#sort').addEventListener('change',render);","window.addEventListener('margen-sort',render);")
s=re.sub(r'<select data-status=.*?</select>','<button class="status-pill" data-cycle="${b.id}" aria-label="Cambiar estado de ${b.title}">${shelf[b.id]} ↻</button>',s)
s=s.replace('if(t.dataset.remove)',"if(t.dataset.cycle){const id=t.dataset.cycle;const states=['Por leer','Leyendo','Leído'];shelf[id]=states[(states.indexOf(shelf[id])+1)%3];persist();renderShelf()}if(t.dataset.remove)")
p.write_text(s,encoding='utf-8')
p=pathlib.Path('index.html');s=p.read_text(encoding='utf-8-sig')
s=s.replace('<script src="app.js" defer></script>','<script type="module" src="main.jsx"></script>')
s=re.sub(r'<label>Ordenar por <select id="sort">.*?</select></label>','<div id="sort-control"></div>',s)
s=s.replace('<button data-filter="Ensayo">Ensayo</button>','').replace('12 historias por descubrir','4 libros para abrir y leer').replace('01 / 12','01 / 04')
s=s.replace('HERMANN<br>HESSE','MIGUEL DE<br>CERVANTES').replace('<strong>Siddhartha</strong>','<strong>Don Quijote</strong>').replace('VIRGINIA WOOLF','BENITO PÉREZ GALDÓS').replace('<strong>Una habitación<br>propia</strong>','<strong>Marianela</strong>').replace('Curaduría independiente. Lecturas extraordinarias.','Libros completos. Lectura libre.')
s=s.replace('<div class="toast"','<div id="reader-root"></div><div class="toast"')
p.write_text(s,encoding='utf-8')
