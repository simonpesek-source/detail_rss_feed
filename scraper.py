import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Zde nastavíme URL (německou nebo anglickou verzi)
url = 'https://www.detail.de/de_de/architektur'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

rss_items = ""

# Procházení článků (struktura tagů se možná bude muset upravit podle reálného webu)
# Předpokládáme, že články jsou v nějakém bloku, například <article> nebo specifickém <div>
for article in soup.find_all('article')[:10]: 
    title_element = article.find('h3') # nebo h2
    link_element = article.find('a')
    
    if title_element and link_element:
        title = title_element.text.strip()
        link = link_element['href']
        
        # Ošetření relativních odkazů
        if link.startswith('/'):
            link = 'https://www.detail.de' + link
            
        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
        </item>"""

# Sestavení finálního XML
rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>DETAIL Magazine - Architektur</title>
  <link>{url}</link>
  <description>Nejnovější architektonické projekty</description>
  <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
  {rss_items}
</channel>
</rss>"""

# Uložení do souboru
with open('feed.xml', 'w', encoding='utf-8') as f:
    f.write(rss_feed)
    
print("RSS feed byl úspěšně vygenerován.")
