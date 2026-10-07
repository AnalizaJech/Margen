import urllib.request,re,pathlib
for num in [2000,17340,10814,25956]:
    url=f'https://www.gutenberg.org/cache/epub/{num}/pg{num}-images.html'
    text=urllib.request.urlopen(url,timeout=30).read().decode()
    imgs=re.findall(r'<img[^>]+src="([^"]+)"',text)
    print(num,imgs[:5])
