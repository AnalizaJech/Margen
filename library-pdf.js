import {jsPDF} from 'jspdf';
import {readingStatus} from './reader-model.js';

export function bookUrl(id, href=window.location.href) {
  const url=new URL(href);url.search='';url.hash='';url.searchParams.set('libro',id);return url.href;
}

// Vector covers stay crisp when printed; each entire cover is a PDF link.
export function createLibraryPdf(books, href=window.location.href) {
  const pdf=new jsPDF({unit:'mm',format:'a5',compress:true});
  pdf.setProperties({title:'Mi biblioteca · Margen',author:'Margen',subject:'Biblioteca personal con enlaces de lectura'});
  books.forEach((book,index)=>{
    if(index)pdf.addPage();
    const status=readingStatus(book.position),url=bookUrl(book.id,href);
    pdf.setFillColor('#f6f3e9');pdf.rect(0,0,148,210,'F');
    pdf.setTextColor('#33452f');pdf.setFont('helvetica','bold');pdf.setFontSize(9);
    pdf.text('M A R G E N',15,17);
    pdf.setFont('helvetica','normal');pdf.setFontSize(7);pdf.text('MI BIBLIOTECA',133,17,{align:'right'});
    pdf.setDrawColor('#ced0bf');pdf.line(15,23,133,23);
    pdf.setFont('times','italic');pdf.setFontSize(14);pdf.text('Historias que se quedan contigo.',15,33);
    const x=33,y=43,w=82,h=117;
    pdf.setFillColor('#ddd9cd');pdf.rect(x+2,y+2,w,h,'F');
    pdf.setFillColor(book.colors[1]);pdf.rect(x,y,w,h,'F');
    pdf.setDrawColor(book.colors[3]);pdf.setFillColor(book.colors[3]);pdf.setLineWidth(1.4);
    const cx=x+w/2,cy=y+82;
    // Each edition keeps its palette and a distinctive geometric motif.
    switch(book.id%5){
      case 0:pdf.circle(cx,cy,25,'F');break;
      case 1:pdf.roundedRect(cx-19,cy-31,38,58,19,19,'F');pdf.rect(cx-19,cy,38,27,'F');pdf.setDrawColor(book.colors[2]);pdf.setLineWidth(3);pdf.roundedRect(cx-17,cy-29,34,54,16,16,'S');break;
      case 2:{const a=35*Math.PI/180,r=24;const corners=[[-r,-r],[r,-r],[r,r],[-r,r]].map(([dx,dy])=>[cx+dx*Math.cos(a)-dy*Math.sin(a),cy+dx*Math.sin(a)+dy*Math.cos(a)]);pdf.lines(corners.slice(1).map((p,i)=>[p[0]-corners[i][0],p[1]-corners[i][1]]),corners[0][0],corners[0][1],[1,1],'F',true);break;}
      case 3:for(let offset=-25;offset<=25;offset+=5.5){const half=Math.sqrt(26*26-offset*offset);pdf.rect(cx-half,cy+offset,half*2,1.6,'F');}break;
      default:pdf.lines([[0,-29,26,-29,26,0],[0,29,-26,29,-26,0]],cx-13,cy,[1,1],'F',true);break;
    }
    pdf.setTextColor(book.colors[2]);pdf.setFont('helvetica','normal');pdf.setFontSize(7);
    pdf.text(pdf.splitTextToSize(book.author.toUpperCase(),w-16),x+8,y+11);
    pdf.setFont('times','normal');pdf.setFontSize(book.title.length>23?22:28);
    pdf.text(pdf.splitTextToSize(book.title,w-16),x+8,y+29,{lineHeightFactor:1.05});
    pdf.setFont('helvetica','normal');pdf.setFontSize(6);pdf.text(`MARGEN / ${book.id}`,x+8,y+h-8);
    pdf.link(x,y,w,h,{url});
    pdf.setTextColor('#33452f');pdf.setFontSize(8);pdf.setFont('helvetica','bold');
    pdf.text(status.label.toUpperCase(),15,175);
    pdf.setFont('helvetica','normal');pdf.text(book.position?`Página ${book.position.page+1} · ${status.percent}% recorrido`:'Una historia por comenzar',133,175,{align:'right'});
    pdf.setFillColor('#33452f');pdf.roundedRect(15,181,118,11,2,2,'F');
    pdf.setTextColor('#f6f3e9');pdf.setFontSize(9);pdf.text('ABRIR ESTE LIBRO EN MARGEN',74,188,{align:'center'});
    pdf.link(15,181,118,11,{url});
    pdf.setTextColor('#747b6c');pdf.setFontSize(6);pdf.text('Portada y botón contienen un enlace a la edición completa.',74,199,{align:'center'});
    pdf.text(`${index+1} / ${books.length}`,133,204,{align:'right'});
  });
  return pdf;
}

export function exportLibrary(books) {
  if(books.length)createLibraryPdf(books).save('Mi-biblioteca-Margen.pdf');
}
