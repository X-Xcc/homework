/**
 * SSE (Server-Sent Events) 流式请求辅助函数。
 * 手动解析 text/event-stream 格式，逐 chunk 回调。
 */
import { authStore } from './auth-store';

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '';

export type SSEOptions = {
  /** 不带 token（如匿名场景） */
  skipAuth?: boolean;
};

/**
 * 发起 SSE 流式请求，逐 chunk 调用 onChunk。
 * 返回完整拼接的文本。
 */
export async function streamSSE(
  path: string,
  body: unknown,
  onChunk: (text: string) => void,
  options: SSEOptions = {},
): Promise<string> {
  const token = options.skipAuth ? null : authStore.getAccessToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = path.startsWith('http') ? path : `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`;

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = `请求失败: ${response.status}`;
    try {
      const errData = await response.json();
      if (errData?.detail) detail = errData.detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('无法读取流式响应');
  }

  const decoder = new TextDecoder();
  let fullText = '';
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    // 最后一行可能不完整，保留到下次
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith('data: ')) continue;

      const data = trimmed.slice(6);
      if (data === '[DONE]') continue;

      try {
        const parsed = JSON.parse(data) as { content?: string; result?: unknown };
        if (parsed.content) {
          fullText += parsed.content;
          onChunk(parsed.content);
        }
      } catch {
        // 非 JSON 行，跳过
      }
    }
  }

  return fullText;
}
