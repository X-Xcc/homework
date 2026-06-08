import httpx, json, asyncio, os

url = 'https://token-plan-cn.xiaomimimo.com/v1/chat/completions'
headers = {
    'Authorization': 'Bearer tp-cn49tfohal1vgw7bdyjupxhkczd85rl6rgnw1k80k8huoaao',
    'Content-Type': 'application/json'
}

DATA_DIR = 'D:/homework/legal-ai/backend/data'

async def call_mimo(prompt):
    payload = {
        'model': 'mimo-v2.5-pro',
        'max_tokens': 4000,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.1
    }
    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            content = r.json()['choices'][0]['message']['content']
            if content.startswith('```'):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1])
            return content.strip()
    return None

async def gen_batch(prompt, filename, label):
    print(f'  生成{label}...')
    r = await call_mimo(prompt)
    if r:
        try:
            data = json.loads(r)
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f'  OK: {len(data)}条')
            return data
        except:
            print(f'  JSON解析失败，跳过')
    else:
        print(f'  API失败，跳过')
    return []

async def main():
    all_criminal = []
    all_civil = []

    # 刑法 - 总则
    d = await gen_batch("""生成刑法总则5条JSON数组。
格式：[{"id":"c1","chapter":"总则","article_number":"第X条","title":"标题","content":"原文","crime_name":"","judicial_interpretations":[],"related_cases":[]}]
包含：第3条罪刑法定、第13条犯罪概念、第14条故意犯罪、第17条刑事责任年龄、第20条正当防卫。只返回JSON。""", 'batch1.json', '刑法总则(1)')
    all_criminal.extend(d)

    # 刑法 - 总则续
    d = await gen_batch("""生成刑法总则5条JSON数组，格式同上。
包含：第33条主刑种类、第48条死刑、第67条自首、第72条缓刑、第87条追诉时效。只返回JSON。""", 'batch2.json', '刑法总则(2)')
    all_criminal.extend(d)

    # 刑法 - 人身权
    d = await gen_batch("""生成刑法侵犯人身权利罪5条JSON数组，格式同上。
包含：第232条故意杀人、第233条过失致人死亡、第234条故意伤害、第236条强奸、第238条非法拘禁。只返回JSON。""", 'batch3.json', '刑法人身权')
    all_criminal.extend(d)

    # 刑法 - 人身权续
    d = await gen_batch("""生成刑法侵犯人身权利罪5条JSON数组，格式同上。
包含：第243条诬告陷害、第246条侮辱诽谤、第260条虐待、第240条拐卖妇女儿童、第239条绑架。只返回JSON。""", 'batch4.json', '刑法人身权(2)')
    all_criminal.extend(d)

    # 刑法 - 财产权
    d = await gen_batch("""生成刑法侵犯财产罪5条JSON数组，格式同上。
包含：第263条抢劫、第264条盗窃、第266条诈骗、第267条抢夺、第270条侵占。只返回JSON。""", 'batch5.json', '刑法财产权')
    all_criminal.extend(d)

    # 刑法 - 财产权续
    d = await gen_batch("""生成刑法侵犯财产罪4条JSON数组，格式同上。
包含：第271条职务侵占、第274条敲诈勒索、第275条故意毁坏财物、第276条破坏生产经营。只返回JSON。""", 'batch6.json', '刑法财产权(2)')
    all_criminal.extend(d)

    # 刑法 - 其他
    d = await gen_batch("""生成刑法其他常见罪名6条JSON数组，格式同上。
包含：第133条交通肇事、第133条之一危险驾驶、第293条寻衅滋事、第347条毒品犯罪、第382条贪污、第385条受贿。只返回JSON。""", 'batch7.json', '刑法其他')
    all_criminal.extend(d)

    # 统一编号保存
    for i, item in enumerate(all_criminal):
        item['id'] = f'criminal_{i+1}'

    with open(os.path.join(DATA_DIR, 'criminal_law.json'), 'w', encoding='utf-8') as f:
        json.dump(all_criminal, f, ensure_ascii=False, indent=2)
    print(f'\n刑法合计: {len(all_criminal)}条')

    # 民法典 - 物权+合同
    d = await gen_batch("""生成民法典常用条文5条JSON数组。
格式：[{"id":"v1","chapter":"编名","article_number":"第X条","title":"标题","content":"原文","judicial_interpretations":[],"related_cases":[]}]
包含：第143条民事法律行为有效、第465条合同定义、第577条违约责任、第585条违约金、第675条借款返还。只返回JSON。""", 'batch8.json', '民法典合同')
    all_civil.extend(d)

    # 民法典 - 合同续+人格权
    d = await gen_batch("""生成民法典常用条文5条JSON数组，格式同上。
包含：第703条租赁定义、第990条人格权定义、第1032条隐私权、第1062条夫妻共同财产、第1076条协议离婚。只返回JSON。""", 'batch9.json', '民法典人格婚姻')
    all_civil.extend(d)

    # 民法典 - 继承+侵权
    d = await gen_batch("""生成民法典常用条文5条JSON数组，格式同上。
包含：第1079条诉讼离婚、第1127条继承顺序、第1130条继承份额、第1165条过错责任、第1179条人身损害赔偿。只返回JSON。""", 'batch10.json', '民法典继承侵权')
    all_civil.extend(d)

    # 统一编号保存
    for i, item in enumerate(all_civil):
        item['id'] = f'civil_{i+1}'

    with open(os.path.join(DATA_DIR, 'civil_law.json'), 'w', encoding='utf-8') as f:
        json.dump(all_civil, f, ensure_ascii=False, indent=2)
    print(f'民法典合计: {len(all_civil)}条')

    # 清理临时文件
    for f in os.listdir(DATA_DIR):
        if f.startswith('batch') and f.endswith('.json'):
            os.remove(os.path.join(DATA_DIR, f))

    print('\n完成!')

asyncio.run(main())
