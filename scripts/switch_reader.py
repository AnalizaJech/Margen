import pathlib
p=pathlib.Path('main.jsx');s=p.read_text(encoding='utf-8-sig');start=s.index('function paginate(');end=s.index("createRoot(document.getElementById('sort-control'))");s=s[:start]+s[end:];s=s.replace("import {PageFlip} from 'page-flip';","import Reader from './Reader.jsx';");p.write_text(s,encoding='utf-8',newline='\n')
