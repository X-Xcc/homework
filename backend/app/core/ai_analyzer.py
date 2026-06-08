import httpx
import json
from typing import List, Optional, AsyncGenerator
from app.config import settings

class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.MIMO_API_KEY
        self.api_url = settings.MIMO_API_URL
        self.model = settings.MIMO_MODEL

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _call_api(self, messages: List[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.api_url, headers=self._get_headers(), json=payload)

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")

    async def _call_api_stream(self, messages: List[dict], temperature: float = 0.7, max_tokens: int = 4096) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", self.api_url, headers=self._get_headers(), json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def chat(self, message: str, history: List[dict] = None, context: str = None) -> str:
        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"你是一位专业的中国法律顾问。以下是相关法律背景：\n{context}"
            })
        else:
            messages.append({
                "role": "system",
                "content": "你是一位专业的中国法律顾问，精通刑法、民法典等中国法律。请用专业但易懂的方式回答用户的法律问题。"
            })

        if history:
            for msg in history[-10:]:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        messages.append({"role": "user", "content": message})

        try:
            return await self._call_api(messages, temperature=0.7)
        except Exception as e:
            return f"抱歉，请求出错: {str(e)}"

    async def chat_stream(self, message: str, history: List[dict] = None, context: str = None) -> AsyncGenerator[str, None]:
        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"你是一位专业的中国法律顾问。以下是相关法律背景：\n{context}"
            })
        else:
            messages.append({
                "role": "system",
                "content": "你是一位专业的中国法律顾问，精通刑法、民法典等中国法律。请用专业但易懂的方式回答用户的法律问题。"
            })

        if history:
            for msg in history[-10:]:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        messages.append({"role": "user", "content": message})

        try:
            async for chunk in self._call_api_stream(messages, temperature=0.7):
                yield chunk
        except Exception as e:
            yield f"错误: {str(e)}"

    async def analyze_contract(self, text: str) -> dict:
        prompt = """你是一位专业的中国法律顾问。请分析以下合同文本，找出其中的法律风险。

请严格按照以下JSON格式返回分析结果，不要添加任何其他内容：
{
    "risks": [
        {
            "level": "high",
            "title": "风险标题",
            "description": "风险描述",
            "location": "所在条款位置",
            "legal_basis": ["相关法律依据"],
            "suggestion": "修改建议"
        }
    ],
    "summary": "整体分析总结"
}

注意：
1. level只能是high、medium、low之一
2. legal_basis是数组，包含相关法条名称
3. 请用中文回答
"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"请分析以下合同：\n\n{text[:6000]}"}
        ]

        try:
            content = await self._call_api(messages, temperature=0.3)
            return self._parse_json(content)
        except Exception as e:
            return {"risks": [], "summary": f"分析出错: {str(e)}"}

    async def analyze_contract_stream(self, text: str) -> AsyncGenerator[str, None]:
        prompt = """你是一位专业的中国法律顾问。请分析以下合同文本，找出其中的法律风险。

请严格按照以下JSON格式返回分析结果，不要添加任何其他内容：
{
    "risks": [
        {
            "level": "high",
            "title": "风险标题",
            "description": "风险描述",
            "location": "所在条款位置",
            "legal_basis": ["相关法律依据"],
            "suggestion": "修改建议"
        }
    ],
    "summary": "整体分析总结"
}

注意：
1. level只能是high、medium、low之一
2. legal_basis是数组，包含相关法条名称
3. 请用中文回答
"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"请分析以下合同：\n\n{text[:6000]}"}
        ]

        try:
            async for chunk in self._call_api_stream(messages, temperature=0.3):
                yield chunk
        except Exception as e:
            yield json.dumps({"risks": [], "summary": f"分析出错: {str(e)}"}, ensure_ascii=False)

    async def compare_documents(self, text_a: str, text_b: str) -> dict:
        prompt = """请比较以下两份法律文档的差异，并返回JSON格式的比较结果。

格式：
{
    "changes": [
        {
            "type": "modify",
            "original": "原文内容",
            "modified": "修改后内容",
            "location": "所在位置描述"
        }
    ],
    "summary": "修改总结"
}

type只能是：modify（修改）、add（新增）、delete（删除）
"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"文档A（原文）：\n{text_a[:3000]}\n\n文档B（修改后）：\n{text_b[:3000]}"}
        ]

        try:
            content = await self._call_api(messages, temperature=0.3)
            return self._parse_json(content)
        except Exception as e:
            return {"changes": [], "summary": f"比较出错: {str(e)}"}

    def _parse_json(self, content: str) -> dict:
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except:
            return {"risks": [], "summary": content}

ai_analyzer = AIAnalyzer()
