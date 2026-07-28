import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = 'https://www.detail.de/de_de/'

# Kompletní hlavičky prohlížeče, aby nás web neblokoval
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

rss_items = ""
count = 0

try:
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=15)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Podle tvého HTML kódu jsou články přesně v 'li.article-item'
    articles = soup.find_all('li', class_='article-item')
    seen_links = set()
    
    for article in articles:
        # Hledáme odkaz a nadpis
        link_tag = article.find('a', class_='product-item-link')
        if not link_tag:
            continue
            
        link = link_tag.get('href', '')
        
        # Hledáme nadpis v h3
        title_tag = article.find('h3')
        title = title_tag.text.strip() if title_tag else link_tag.get_text(strip=True)
        
        # Hledáme krátký popis (perex) článku
        desc_tag = article.find('p')
        description = desc_tag.text.strip() if desc_tag else ""
        
        if link and link not in seen_links:
            seen_links.add(link)
            count += 1
            
            # Bezpečné ošetření znaků pro XML
            clean_title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            clean_desc = description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            rss_items += f"""
        <item>
            <title>{clean_title}</title>
            <link>{link}</link>
            <guid>{link}</guid>
            <description>{clean_desc}</description>
        </item>"""

except Exception as e:
    print(f"Chyba při stahování: {e}")

# Vygenerování platného RSS XML
rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>DETAIL Magazine</title>
  <link>{url}</link>
  <description>Nejnovější architektonické projekty a články z Detail.de</description>
  <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
  {rss_items}
</channel>
</rss>"""

with open('feed.xml', 'w', encoding='utf-8') as f:
    f.write(rss_feed)

print(f"Úspěšně vygenerováno {count} článků do RSS.")
