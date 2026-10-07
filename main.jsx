import React, {useState,useEffect,useRef} from 'react';
import {createRoot} from 'react-dom/client';
import Reader from './Reader.jsx';
import {initialize} from './app.js';
import Shell from './shell.jsx';
import {flushSync} from 'react-dom';
flushSync(()=>createRoot(document.getElementById('app')).render(React.createElement(Shell)));
initialize();
import './reader.css';
const h=React.createElement;
function Sort(){const [open,setOpen]=useState(false),[value,setValue]=useState('curated');const ref=useRef();const options={curated:'Selección Margen',title:'Título A–Z'};useEffect(()=>{const close=e=>{if(!ref.current?.contains(e.target))setOpen(false)};document.addEventListener('click',close);return()=>document.removeEventListener('click',close)},[]);return h('div',{className:'custom-select',ref},h('button',{'aria-expanded':open,'aria-haspopup':'menu',onClick:()=>setOpen(!open),onKeyDown:e=>{if(e.key==='Escape')setOpen(false)}},'Ordenar: ',options[value],' ⌄'),open&&h('div',{role:'menu',className:'select-menu'},Object.entries(options).map(([id,label])=>h('button',{key:id,role:'menuitemradio','aria-checked':value===id,onClick:()=>{setValue(id);setOpen(false);window.margenSort=id;window.dispatchEvent(new Event('margen-sort'))}},label,value===id?' ✓':''))))}
createRoot(document.getElementById('sort-control')).render(h(Sort));
createRoot(document.getElementById('reader-root')).render(h(Reader));

