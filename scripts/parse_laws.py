import httpx, json, asyncio, re

DATA_DIR = 'D:/homework/legal-ai/backend/data'

CRIMINAL_URLS = [
    'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/criminal-law/criminal-law/01-general-provisions.md',
    'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/criminal-law/criminal-law/02-specific-provisions.md',
]

CIVIL_URL = 'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/'

async def fetch(url):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.get(url)
        if r.status_code == 200:
            return r.text
    return None

def parse_articles(text, law_name):
    articles = []
    pattern = r'\*\*(第[一二三四五六七八九十百千零〇０-９\d]+条(?:之[一二三四五六七八九十\d]+)?)\*\*\s*(.*?)(?=\*\*第[一二三四五六七八九十百千零〇０-９\d]+条|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    for article_num, content in matches:
        content = content.strip()
        if not content:
            continue

        chapter = ""
        chapter_match = re.search(r'##\s+(第[一二三四五六七八九十\d]+[编章节])\s*(.*)', text[:text.find(f'**{article_num}**')])
        if chapter_match:
            chapter = f"{chapter_match.group(1)} {chapter_match.group(2).strip()}"

        articles.append({
            "id": f"{law_name}_{len(articles)+1}",
            "chapter": chapter,
            "article_number": article_num,
            "title": "",
            "content": content,
            "crime_name": "",
            "judicial_interpretations": [],
            "related_cases": []
        })

    return articles

async def main():
    print("下载刑法数据...")
    all_criminal = []

    for url in CRIMINAL_URLS:
        text = await fetch(url)
        if text:
            articles = parse_articles(text, "criminal")
            all_criminal.extend(articles)
            print(f"  解析 {len(articles)} 条")

    for i, item in enumerate(all_criminal):
        item['id'] = f'criminal_{i+1}'

    with open(f'{DATA_DIR}/criminal_law.json', 'w', encoding='utf-8') as f:
        json.dump(all_criminal, f, ensure_ascii=False, indent=2)
    print(f"刑法合计: {len(all_criminal)}条")

    print("\n下载民法典数据...")
    civil_urls = [
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/01-general-provisions.md',
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/02-property-rights.md',
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/03-contracts.md',
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/04-personality-rights.md',
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/05-marriage-family.md',
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/06-succession.md',
        'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/07-tort-liability.md',
    ]

    all_civil = []
    for url in civil_urls:
        text = await fetch(url)
        if text:
            articles = parse_articles(text, "civil")
            all_civil.extend(articles)
            print(f"  解析 {len(articles)} 条")

    for i, item in enumerate(all_civil):
        item['id'] = f'civil_{i+1}'

    with open(f'{DATA_DIR}/civil_law.json', 'w', encoding='utf-8') as f:
        json.dump(all_civil, f, ensure_ascii=False, indent=2)
    print(f"民法典合计: {len(all_civil)}条")

    print("\n完成!")

asyncio.run(main())
