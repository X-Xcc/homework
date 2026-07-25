import httpx, json, asyncio, re

DATA_DIR = 'D:/homework/legal-ai/backend/data'

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
            "judicial_interpretations": [],
            "related_cases": []
        })

    return articles

async def main():
    print("下载民法典数据...")
    civil_urls = [
        ('01-general-principles.md', '总则编'),
        ('02-property-rights.md', '物权编'),
        ('03-contracts.md', '合同编'),
        ('04-personality-rights.md', '人格权编'),
        ('05-marriage-and-family.md', '婚姻家庭编'),
        ('06-inheritance.md', '继承编'),
        ('07-tort-liability.md', '侵权责任编'),
    ]

    all_civil = []
    for filename, chapter_name in civil_urls:
        url = f'https://raw.githubusercontent.com/ImCa0/just-laws/master/docs/civil-and-commercial/civil-code/{filename}'
        text = await fetch(url)
        if text:
            articles = parse_articles(text, "civil")
            for a in articles:
                if not a['chapter']:
                    a['chapter'] = chapter_name
            all_civil.extend(articles)
            print(f"  {chapter_name}: {len(articles)}条")
        else:
            print(f"  {chapter_name}: 下载失败")

    for i, item in enumerate(all_civil):
        item['id'] = f'civil_{i+1}'

    with open(f'{DATA_DIR}/civil_law.json', 'w', encoding='utf-8') as f:
        json.dump(all_civil, f, ensure_ascii=False, indent=2)
    print(f"\n民法典合计: {len(all_civil)}条")
    print("完成!")

asyncio.run(main())
