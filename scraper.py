import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = 'https://www.detail.de/de_de/architektur'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

rss_items = ""
count = 0

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.encoding = 'utf-8'
    
    # Použijeme odolnější lxml parser
    soup = BeautifulSoup(response.text, 'lxml')
    
    seen_links = set()
    
    # Vyhledáme všechny odkazové značky na stránce
    for a in soup.find_all('a', href=True):
        href = a['href']
        title = a.get_text(strip=True)
        
        # Filtrujemy pouze relevantní odkazy na projekty/články
        if href and len(title) > 15: # Ignorujeme krátké odkazové texty jako "Více", "Home" atd.
            if href.startswith('/'):
                full_url = 'https://www.detail.de' + href
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # Vyfiltrujeme duplicity a nerelevantní systémy
            if full_url not in seen_links and 'detail.de' in full_url:
                seen_links.add(full_url)
                count += 1
                
                # Vyčištění titulku pro XML
                clean_title = title.replace('<', '').replace('>', '').replace('&', '&amp;')
                
                rss_items += f"""
        <item>
            <title>{clean_title}</title>
            <link>{full_url}</link>
            <guid>{full_url}</guid>
        </item>"""
                
                if count >= 20: # Uložíme 20 nejnovějších
                    break

except Exception as e:
    print(f"Chyba při stahování: {e}")

# Sestavení XML feedu i v případě chyb (aby skript nikdy nespadl s Exit Code 1)
rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>DETAIL Magazine</title>
  <link>{url}</link>
  <description>Nejnovější články z Detail.de</description>
  <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
  {rss_items}
</channel>
</rss>"""

with open('feed.xml', 'w', encoding='utf-8') as f:
    f.write(rss_feed)

print(f"HOTOVO: Vygenerováno {count} položek.")
