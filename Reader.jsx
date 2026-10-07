import React, {useEffect, useRef, useState} from 'react';
import {PageFlip} from 'page-flip';
import {flipPoint, migratePosition} from './reader-model.js';

const get = (key, fallback) => {try {return JSON.parse(localStorage.getItem(key)) ?? fallback;} catch {return fallback;}};
const set = (key, value) => {try {localStorage.setItem(key, JSON.stringify(value));} catch {}};
const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const base = import.meta.env.BASE_URL;

export default function Reader() {
  const [book, setBook] = useState(null), [edition, setEdition] = useState(null);
  const [page, setPage] = useState(0), [loading, setLoading] = useState(false), [error, setError] = useState('');
  const [night, setNight] = useState(get('margen-night', false)), [indexOpen, setIndexOpen] = useState(false);
  const [bookmark, setBookmark] = useState(-1), [busy, setBusy] = useState(false), [portrait, setPortrait] = useState(false);
  const stage = useRef(null), engine = useRef(null), dialog = useRef(null), opener = useRef(null), initial = useRef(0);
  const gesture = useRef(null), skipClick = useRef(false), abort = useRef(null);
  const pages = edition?.pages || [], chapters = edition?.chapters || [];
  const remember = (id, p, total) => {
    const previous=get('margen-position-'+id,{});
    const contentEnd=edition?.chapters.find(c=>/créditos y licencia/i.test(c.title))?.page ?? total;
    const visible=engine.current?.getOrientation()==='portrait'?1:2;
    set('margen-position-'+id, {version:3,page:p,total,contentEnd,furthestPage:Math.max(previous.furthestPage??previous.page??0,p),completed:previous.completed===true || p+visible>=contentEnd});
    set('margen-progress-'+id,p);
    window.dispatchEvent(new Event('margen-progress'));
  };

  useEffect(() => {
    const open = async event => {
      abort.current?.abort();const controller = new AbortController();abort.current = controller;
      const request = typeof event.detail === 'object' ? event.detail : {id:event.detail};
      const next = window.margenBooks.find(b => b.id === request.id);if (!next) return;
      opener.current = document.activeElement;setBook(next);setEdition(null);setLoading(true);setError('');setIndexOpen(false);setBusy(false);
      try {
        const response = await fetch(`${base}books/${next.id}.json`, {signal:controller.signal});
        if (!response.ok) throw new Error('Edition unavailable');
        const data = await response.json();if(controller.signal.aborted)return;
        const position = get('margen-position-'+next.id, null);
        initial.current = Math.max(0, Math.min(request.page ?? (position?.version===3 ? position.page : migratePosition(data,get('margen-progress-'+next.id,0))), data.pages.length-1));
        const savedBookmark = get('margen-bookmark-v3-'+next.id, null);
        const previousBookmark = get('margen-bookmark-'+next.id, -1);
        const mark = savedBookmark ?? (previousBookmark>=0 ? migratePosition(data,previousBookmark) : -1);
        setBookmark(mark);set('margen-bookmark-v3-'+next.id,mark);setEdition(data);
      } catch (err) {if(err.name!=='AbortError')setError('No pudimos cargar esta edición. Cierra el lector y vuelve a intentarlo.');}
      finally {if(!controller.signal.aborted)setLoading(false);}
    };
    window.addEventListener('margen-read',open);
    const linked=Number(new URLSearchParams(location.search).get('libro'));
    if(window.margenBooks.some(b=>b.id===linked))window.dispatchEvent(new CustomEvent('margen-read',{detail:linked}));
    return () => {abort.current?.abort();window.removeEventListener('margen-read',open);};
  },[]);

  useEffect(() => {
    if(!book)return;dialog.current.showModal();dialog.current.scrollTop=0;
    return () => {dialog.current?.close();opener.current?.isConnected && opener.current.focus();};
  },[book]);

  useEffect(() => {
    if(!edition || !stage.current)return;
    const mount = document.createElement('div');mount.className='book-engine';stage.current.append(mount);
    for(let i=0;i<edition.pages.length;i++) {
      const p=edition.pages[i], node=document.createElement('article');node.className='paper-page';node.dataset.page=String(i);
      if(p.type==='cover') {
        node.classList.add('reader-cover');node.style.cssText=`--cover:${book.colors[1]};--cover-text:${book.colors[2]}`;
        node.innerHTML=`<div class="reader-cover-inner"><span>MARGEN / BIBLIOTECA</span><h3>${esc(book.title)}</h3><div class="cover-emblem" aria-hidden="true">✳</div><p>${esc(book.author)}</p><small>EDICIÓN COMPLETA · LECTURA LIBRE</small></div>`;
      } else {
        node.innerHTML=`<div class="paper-inner"><div class="running-head">${esc(book.title)}</div><div class="page-text">${p.blocks.map(b=>`<${b.kind==='heading'?'h3':'p'} class="block-${b.kind}">${esc(b.text)}</${b.kind==='heading'?'h3':'p'}>`).join('')}</div><span class="folio">${i+1}</span></div>`;
      }
      mount.append(node);
    }
    const maxHeight=Math.max(350,Math.min(590,window.innerHeight-280));
    const flip=new PageFlip(mount,{width:350,height:510,size:'stretch',minWidth:Math.min(320,window.innerWidth-40),maxWidth:Math.min(420,maxHeight*350/510),minHeight:340,maxHeight,showCover:false,autoSize:true,usePortrait:true,maxShadowOpacity:.3,flippingTime:matchMedia('(prefers-reduced-motion: reduce)').matches?1:680,useMouseEvents:false,showPageCorners:false,startPage:initial.current});
    engine.current=flip;
    flip.on('flip',event=>{setPage(event.data);remember(book.id,event.data,edition.pages.length);});
    flip.on('changeState',event=>setBusy(event.data==='flipping'));
    flip.on('changeOrientation',event=>setPortrait(event.data==='portrait'));
    flip.loadFromHTML(mount.querySelectorAll('.paper-page'));
    setPage(flip.getCurrentPageIndex());setPortrait(flip.getOrientation()==='portrait');remember(book.id,flip.getCurrentPageIndex(),edition.pages.length);
    const rescale=()=>{const bounds=flip.getBoundsRect();mount.style.setProperty('--paper-scale',String(bounds.pageWidth/350));dialog.current?.style.setProperty('--reader-book-width',`${bounds.pageWidth*(flip.getOrientation()==='portrait'?1:2)}px`);};
    const observer=new ResizeObserver(rescale);observer.observe(mount);rescale();
    return()=>{observer.disconnect();flip.getUI().removeHandlers();flip.destroy();engine.current=null;};
  },[edition,book]);

  function turn(direction) {
    const flip=engine.current;if(!flip||flip.getState()==='flipping')return;
    const p=flip.getCurrentPageIndex(), step=flip.getOrientation()==='portrait'?1:2;
    if(direction<0 && p===0 || direction>0 && p+step>=pages.length)return;
    // Use the visible page edge in both modes; the library's previous-page helper
    // assumes x=10 even when the book is horizontally offset.
    flip.getFlipController().flip(flipPoint(flip.getBoundsRect(),flip.getOrientation(),direction));
  }
  function jump(target) {
    const flip=engine.current;if(!flip||flip.getState()==='flipping')return;
    flip.turnToPage(target);const p=flip.getCurrentPageIndex();setPage(p);remember(book.id,p,pages.length);setIndexOpen(false);
  }
  function pointerUp(event) {
    if(!gesture.current)return;const dx=event.clientX-gesture.current.x,dy=event.clientY-gesture.current.y;gesture.current=null;
    if(Math.abs(dx)>40 && Math.abs(dx)>Math.abs(dy)*1.4){skipClick.current=true;turn(dx<0?1:-1);}
  }
  function clickPaper(event) {
    if(skipClick.current){skipClick.current=false;return;}
    if(window.getSelection()?.toString().trim())return;
    const rect=stage.current.getBoundingClientRect();turn(event.clientX<rect.left+rect.width/2?-1:1);
  }
  function note() {
    window.dispatchEvent(new CustomEvent('margen-reader-note',{detail:{id:book.id,title:book.title,page,text:window.getSelection()?.toString()||''}}));
  }
  const close=()=>{abort.current?.abort();setBook(null);setEdition(null);};
  if(!book)return null;
  const activeChapter=chapters.filter(c=>c.page<=page+(portrait?0:1)).at(-1);
  const last=page+(portrait?1:2)>=pages.length;

  return <dialog ref={dialog} className={`reader-dialog ${night?'reader-night':''}`} aria-label={`Lector de ${book.title}`} onCancel={close} onKeyDown={event=>{
    if(['INPUT','TEXTAREA'].includes(event.target.tagName))return;
    if(event.key==='ArrowRight'){event.preventDefault();turn(1);}
    if(event.key==='ArrowLeft'){event.preventDefault();turn(-1);}
  }}>
    <header className="reader-header"><div><span className="eyebrow">MARGEN / SALA DE LECTURA</span><h2>{book.title}</h2><p>{book.author}</p></div><button className="reader-exit" onClick={close} aria-label="Cerrar lector" title="Cerrar lector"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button></header>
    <div className="reader-toolbar"><div>
      <button className="reader-tool" onClick={note} disabled={loading}><span>✎</span> Tomar nota</button>
      <button className="reader-tool" onClick={()=>setIndexOpen(!indexOpen)} aria-expanded={indexOpen} disabled={loading}><span>☷</span> Índice</button>
      <button className={`reader-tool ${bookmark===page?'is-active':''}`} onClick={()=>{const value=bookmark===page?-1:page;setBookmark(value);set('margen-bookmark-v3-'+book.id,value);}} disabled={loading} aria-pressed={bookmark===page}><span>{bookmark===page?'◆':'◇'}</span> {bookmark===page?'Marcado':'Marcar página'}</button>
      {bookmark>=0 && <button className="reader-tool" onClick={()=>jump(bookmark)} disabled={loading}>Ir a p. {bookmark+1} ↗</button>}
    </div><button className="reader-tool theme-tool" onClick={()=>{setNight(!night);set('margen-night',!night);}} aria-pressed={night} aria-label={night?'Activar tema claro':'Activar tema oscuro'} title={night?'Activar tema claro':'Activar tema oscuro'}><svg viewBox="0 0 24 24" aria-hidden="true">{night?<><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></>:<path d="M20 15.5A9 9 0 0 1 8.5 4 9 9 0 1 0 20 15.5Z"/>}</svg></button></div>
    {indexOpen && <aside className="reader-index" aria-label="Índice de lectura"><div className="index-heading"><p className="eyebrow">MAPA DE ESTA HISTORIA</p><button onClick={()=>setIndexOpen(false)} aria-label="Cerrar índice">×</button></div><h3>Índice</h3><button onClick={()=>jump(0)} className={page<2?'current-section':''}><span>Portada y edición</span><small>1</small></button>{chapters.map((chapter,i)=><React.Fragment key={i}>{chapter.group && chapter.group!==chapters[i-1]?.group && <p className="index-group">{chapter.group}</p>}<button className={`${activeChapter===chapter?'current-section':''} ${chapter.level?'index-subsection':''}`} onClick={()=>jump(chapter.page)} aria-current={activeChapter===chapter?'location':undefined}><span>{chapter.title}</span><small>{chapter.page+1}</small></button></React.Fragment>)}</aside>}
    {loading ? <div className="reader-loading"><span>✳</span><h3>Preparando tu próxima historia…</h3><p>Abriendo la edición completa.</p></div> : error ? <p role="alert" className="reader-loading">{error}</p> : <div className="reading-desk">
      <div className="reader-stage" ref={stage} tabIndex={0} aria-label="Páginas del libro. Clic a la izquierda para retroceder y a la derecha para avanzar." onPointerDown={e=>{gesture.current={x:e.clientX,y:e.clientY};skipClick.current=false;}} onPointerUp={pointerUp} onClick={clickPaper} />
      <div className="reader-navigation"><button className="page-turn previous" onClick={()=>turn(-1)} disabled={busy||page===0} aria-label="Página anterior"><span>←</span><small>Anterior</small></button><div><span className="page-counter">{portrait||page+1===pages.length?`Página ${page+1}`:`Páginas ${page+1}–${page+2}`} <i>/ {pages.length}</i></span><div className="reading-progress"><i style={{width:`${Math.round((page+1)/pages.length*100)}%`}}/></div><small className="current-chapter">{activeChapter?.title||'El principio de una historia'}</small></div><button className="page-turn next" onClick={()=>turn(1)} disabled={busy||last} aria-label="Página siguiente"><small>Siguiente</small><span>→</span></button></div>
    </div>}
    <footer className="reader-footer"><span>Tu página se guarda automáticamente.</span><a className="download-pdf" href={`${base}books/${book.id}.pdf`} download={`Margen-${book.title.replace(/[^a-záéíóúñ0-9]+/gi,'-')}.pdf`}><span>↓</span> Descargar edición PDF</a><a href={`https://www.gutenberg.org/ebooks/${book.id}`} target="_blank" rel="noopener">Fuente y créditos ↗</a></footer>
  </dialog>;
}


