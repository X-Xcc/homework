import httpx, json, asyncio

url = 'https://token-plan-cn.xiaomimimo.com/v1/chat/completions'
headers = {
    'Authorization': 'Bearer REDACTED_MIMO_API_KEY',
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
            return r.json()['choices'][0]['message']['content']
    return None

async def main():
    # 加载现有刑法数据
    with open(f'{DATA_DIR}/criminal_law.json', 'r', encoding='utf-8') as f:
        criminal = json.load(f)

    # 加载现有民法典数据
    with open(f'{DATA_DIR}/civil_law.json', 'r', encoding='utf-8') as f:
        civil = json.load(f)

    # 为重要刑法条文添加司法解释和判例
    criminal_interpretations = {
        "第二百三十二条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理故意杀人、故意伤害案件正确适用死刑问题的指导意见》",
                "《全国法院维护农村稳定刑事审判工作座谈会纪要》(1999年)"
            ],
            "related_cases": [
                "于欢案（2017）鲁刑终151号",
                "张扣扣故意杀人案（2019）陕刑终89号"
            ]
        },
        "第二百三十四条": {
            "judicial_interpretations": [
                "《最高人民法院关于常见犯罪的量刑指导意见》(2017)",
                "《人体损伤程度鉴定标准》(2013年)",
                "《公安机关办理伤害案件规定》"
            ],
            "related_cases": [
                "唐慧案（2012）",
                "药家鑫案（2011）陕刑一终字第68号"
            ]
        },
        "第二百六十三条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理抢劫案件具体应用法律若干问题的解释》",
                "《最高人民法院关于审理抢劫、抢夺刑事案件适用法律若干问题的意见》"
            ],
            "related_cases": [
                "许霆案（2008）粤高法刑一终字第5号"
            ]
        },
        "第二百六十四条": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院关于办理盗窃刑事案件适用法律若干问题的解释》(2013)"
            ],
            "related_cases": [
                "许霆ATM机取款案（2008）"
            ]
        },
        "第二百六十六条": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院关于办理诈骗刑事案件具体应用法律若干问题的解释》(2011)"
            ],
            "related_cases": [
                "吴英集资诈骗案（2012）浙刑二终字第30号"
            ]
        },
        "第二十条": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院、公安部关于依法适用正当防卫制度的指导意见》(2020)"
            ],
            "related_cases": [
                "于海明正当防卫案（2018）",
                "于欢案（2017）鲁刑终151号"
            ]
        },
        "第一百三十三条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理交通肇事刑事案件具体应用法律若干问题的解释》(2000)"
            ],
            "related_cases": [
                "孙伟铭醉驾案（2009）川刑终字第258号"
            ]
        },
        "第一百三十三条之一": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院、公安部关于办理醉酒驾驶机动车刑事案件适用法律若干问题的意见》(2013)"
            ],
            "related_cases": [
                "高晓松醉驾案（2011）"
            ]
        },
        "第二百九十三条": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院关于办理寻衅滋事刑事案件适用法律若干问题的解释》(2013)"
            ],
            "related_cases": []
        },
        "第三百八十二条": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院关于办理贪污贿赂刑事案件适用法律若干问题的解释》(2016)"
            ],
            "related_cases": [
                "赖小民受贿案（2021）"
            ]
        },
        "第三百八十五条": {
            "judicial_interpretations": [
                "《最高人民法院、最高人民检察院关于办理贪污贿赂刑事案件适用法律若干问题的解释》(2016)"
            ],
            "related_cases": [
                "周永康受贿案（2015）",
                "令计划受贿案（2016）"
            ]
        }
    }

    # 更新刑法数据
    for item in criminal:
        article_num = item.get("article_number", "")
        if article_num in criminal_interpretations:
            item["judicial_interpretations"] = criminal_interpretations[article_num]["judicial_interpretations"]
            item["related_cases"] = criminal_interpretations[article_num]["related_cases"]

    with open(f'{DATA_DIR}/criminal_law.json', 'w', encoding='utf-8') as f:
        json.dump(criminal, f, ensure_ascii=False, indent=2)
    print(f'刑法已更新: {len(criminal)}条')

    # 为民法典重要条文添加司法解释和判例
    civil_interpretations = {
        "第一百四十三条": {
            "judicial_interpretations": [
                "《最高人民法院关于适用〈中华人民共和国民法典〉总则编若干问题的解释》第18-25条"
            ],
            "related_cases": []
        },
        "第五百七十七条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理买卖合同纠纷案件适用法律问题的解释》",
                "《最高人民法院关于当前形势下审理民商事合同纠纷案件若干问题的指导意见》"
            ],
            "related_cases": []
        },
        "第五百八十五条": {
            "judicial_interpretations": [
                "《最高人民法院关于适用〈中华人民共和国合同法〉若干问题的解释（二）》第28、29条"
            ],
            "related_cases": []
        },
        "第一千零七十九条": {
            "judicial_interpretations": [
                "《最高人民法院关于适用〈中华人民共和国民法典〉婚姻家庭编的解释（一）》"
            ],
            "related_cases": []
        },
        "第一千一百六十五条": {
            "judicial_interpretations": [
                "《最高人民法院关于适用〈中华人民共和国民法典〉侵权责任编的解释（一）》"
            ],
            "related_cases": []
        },
        "第一千一百七十九条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理人身损害赔偿案件适用法律若干问题的解释》"
            ],
            "related_cases": []
        },
        "第一千零六十二条": {
            "judicial_interpretations": [
                "《最高人民法院关于适用〈中华人民共和国民法典〉婚姻家庭编的解释（一）》第24-27条"
            ],
            "related_cases": []
        },
        "第一千零三十二条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理使用人脸识别技术处理个人信息相关民事案件适用法律若干问题的规定》"
            ],
            "related_cases": [
                "全国首例涉人脸识别纠纷案（2021）浙0192民初1695号"
            ]
        },
        "第一千一百二十七条": {
            "judicial_interpretations": [
                "《最高人民法院关于适用〈中华人民共和国民法典〉继承编的解释（一）》第10-15条"
            ],
            "related_cases": []
        },
        "第一千二百三十二条": {
            "judicial_interpretations": [
                "《最高人民法院关于审理生态环境侵权纠纷案件适用惩罚性赔偿的解释》"
            ],
            "related_cases": []
        }
    }

    # 更新民法典数据
    for item in civil:
        article_num = item.get("article_number", "")
        if article_num in civil_interpretations:
            item["judicial_interpretations"] = civil_interpretations[article_num]["judicial_interpretations"]
            item["related_cases"] = civil_interpretations[article_num]["related_cases"]

    with open(f'{DATA_DIR}/civil_law.json', 'w', encoding='utf-8') as f:
        json.dump(civil, f, ensure_ascii=False, indent=2)
    print(f'民法典已更新: {len(civil)}条')

    print('完成!')

asyncio.run(main())
