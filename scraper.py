import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Zde nastavíme URL
url = 'https://www.detail.de/de_de/architektur'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

rss_items = ""

# Web Detail používá pro karty článků odkazové kontejnery nebo třídy s card/teaser
# Hledáme všechny odkazové prvky obsahující nadpisy
cards = soup.select('a[href*="/de_de/"]')

seen_links = set()
count = 0

for card in cards:
    # Získání nadpisu z karty (bývá v h2, h3, h4 nebo přímo v textu odkazu)
    title_element = card.find(['h1', 'h2', 'h3', 'h4', 'span'])
    
    link = card.get('href', '')
    
    if title_element and link:
        title = title_element.text.strip()
        
        # Očištění odkazů a filtrace (chceme jen články, ne navigaci nebo patičku)
        if link.startswith('/'):
            link = 'https://www.detail.de' + link
            
        # Ochrana proti duplicitám a filtrování krátkých textů / balastních odkazů
        if link not in seen_links and len(title) > 10 and '/de_de/' in link:
            seen_links.add(link)
            count += 1
            
            rss_items += f"""
        <item>
            <title><![CDATA[{title}]]></title>
            <link>{link}</link>
            <guid>{link}</guid>
        </item>"""
            
            if count >= 15: # Načteme maximálně 15 nejnovějších článků
                break

# Sestavení XML
rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>DETAIL Magazine - Architektur</title>
  <link>{url}</link>
  <description>Nejnovější architektonické projekty z Detail.de</description>
  <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
  {rss_items}
</channel>
</rss>"""

with open('feed.xml', 'w', encoding='utf-8') as f:
    f.write(rss_feed)

print(f"RSS feed vygenerován s {count} položkami.")
