import pathlib,re
p=pathlib.Path('app.js');s=p.read_text(encoding='utf-8-sig');s=re.sub(r'const books = \[.*?\];','const books = catalog;',s,count=1,flags=re.S);s="import catalog from './catalog.json';\n"+s
s=s.replace('<span>Edición digital</span>','<span>${b.pages} páginas</span>')
s=s.replace('function renderShelf(){', '''function renderShelf(){''')
s=s.replace('<p>${b.author}</p></div><button class="status-pill"', '<p>${b.author}</p><p class="shelf-progress">${readStore("margen-position-"+b.id,null)?`Página ${readStore("margen-position-"+b.id,{}).page+1} de ${b.pages} · ${Math.round((readStore("margen-position-"+b.id,{}).page+1)/b.pages*100)}% leído`:"Tu historia está por comenzar"}</p></div><button class="shelf-resume" data-read="${b.id}">${readStore("margen-position-"+b.id,null)?"Reanudar lectura":"Comenzar lectura"} ↗</button><button class="status-pill"')
s=s.replace('if(t.dataset.read){t.closest(\'dialog\').close();',"if(t.dataset.read){t.closest('dialog')?.close();")
s=s.replace('<small>${escapeHTML(n.date)}</small>', '<small>${escapeHTML(n.date)}${n.page!=null?` · Página ${n.page+1}`:""}</small>')
s=s.replace("notes.unshift({id:crypto.randomUUID(),book,text,date:","const origin=$('#journal-dialog').dataset.reader==='true';notes.unshift({id:crypto.randomUUID(),book,text,...(origin?{bookId:Number($('#journal-dialog').dataset.bookId),page:Number($('#journal-dialog').dataset.page)}:{}),date:")
s=s.replace("renderNotes();toast('Tu descubrimiento se queda contigo')", "renderNotes();if(origin){$('#journal-dialog').close();delete $('#journal-dialog').dataset.reader;}toast('Tu descubrimiento se queda contigo')")
s=s.replace("function openJournal(){renderNotes();", "function openJournal(){renderNotes();")
s=s.replace("window.addEventListener('margen-reader-note',e=>{$('#note-book').value=e.detail.title;$('#note-text').value=e.detail.text||'';openJournal()});", """window.addEventListener('margen-reader-note',e=>{$('#note-book').value=e.detail.title;$('#note-text').value=e.detail.text||'';Object.assign($('#journal-dialog').dataset,{reader:'true',bookId:String(e.detail.id),page:String(e.detail.page)});openJournal();$('#note-text').focus()});
window.addEventListener('margen-read',e=>{const id=typeof e.detail==='object'?e.detail.id:e.detail;if(!shelf[id]){shelf[id]='Leyendo';persist();render();renderShelf()}});
window.addEventListener('margen-progress',renderShelf);
$('#journal-dialog').addEventListener('close',()=>{delete $('#journal-dialog').dataset.reader});""")
p.write_text(s,encoding='utf-8',newline='\n')
p=pathlib.Path('shell.jsx');s=p.read_text(encoding='utf-8-sig').replace('4 libros para abrir y leer','12 libros para abrir y leer').replace('01 / 04','01 / 12').replace('<button data-filter="Clásicos">Clásicos</button>','<button data-filter="Clásicos">Clásicos</button><button data-filter="Cuentos">Cuentos</button><button data-filter="Teatro">Teatro</button>');p.write_text(s,encoding='utf-8',newline='\n')
