import pathlib
p=pathlib.Path('app.js');s=p.read_text(encoding='utf-8-sig');s=s.replace("if(origin){$('#journal-dialog').close();", "if(origin){try{localStorage.removeItem('margen-note-draft-'+$('#journal-dialog').dataset.bookId)}catch{}$('#journal-dialog').close();")
p.write_text(s,encoding='utf-8',newline='\n')
