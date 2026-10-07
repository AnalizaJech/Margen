/** StPageFlip coordinates include a hidden left page in portrait mode. */
export function readingStatus(position) {
  if (!position || !(position.furthestPage ?? position.page)) return {key:'unread',label:'Por leer',percent:0};
  const end=Math.max(1,position.contentEnd ?? position.total);
  const percent=Math.min(100,Math.round(((position.furthestPage ?? position.page)+1)/end*100));
  const completed=position.completed===true || (position.furthestPage ?? position.page)>=end-1;
  return {key:completed?'finished':'reading',label:completed?'Leído':'Leyendo',percent:completed?100:Math.min(99,percent)};
}

export function flipPoint(bounds, orientation, direction) {
  return {
    x: bounds.left + (direction > 0 ? bounds.pageWidth * 2 - 10 : orientation === 'portrait' ? bounds.pageWidth + 10 : 10),
    y: bounds.top + bounds.height - 2,
  };
}

/** Find the text anchor of an old 760-character page after repagination. */
export function migratePosition(data, oldPage) {
  if (!oldPage || !data.paragraphs) return 0;
  let current = '', index = 0, anchor = '';
  outer: for (const paragraph of data.paragraphs) {
    for (const word of paragraph.split(/\s+/)) {
      if ((current + word).length + (current.match(/\n/g) || []).length * 35 > 760) {
        if (index === oldPage) { anchor = current.trim().split(/\s+/).slice(0, 6).join(' ').replace(/[_#]/g, ''); break outer; }
        index++; current = '';
      }
      current += word + ' ';
    }
    current += '\n\n';
  }
  if (anchor) {
    const found = data.pages.findIndex(p => p.blocks.some(b => b.text.includes(anchor)));
    if (found >= 0) return found;
  }
  return Math.min(oldPage, data.pages.length - 1);
}
