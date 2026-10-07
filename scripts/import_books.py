import urllib.request, json, re, pathlib
root = pathlib.Path('public/books')
root.mkdir(parents=True, exist_ok=True)
for num in [2000,17340,10814,25956]:
    url=f'https://www.gutenberg.org/cache/epub/{num}/pg{num}.txt'
    text=urllib.request.urlopen(url, timeout=60).read().decode('utf-8-sig')
    (root/f'{num}-original.txt').write_text(text, encoding='utf-8')
    body=re.split(r'\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n', text, maxsplit=1)[-1]
    body=re.split(r'\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK', body, maxsplit=1)[0]
    paragraphs=[re.sub(r'\s*\n\s*',' ',p).strip() for p in re.split(r'\n\s*\n',body)]
    paragraphs=[p for p in paragraphs if p]
    (root/f'{num}.json').write_text(json.dumps({'source':f'https://www.gutenberg.org/ebooks/{num}','paragraphs':paragraphs},ensure_ascii=False), encoding='utf-8')
    print(num, len(paragraphs), len(text))
