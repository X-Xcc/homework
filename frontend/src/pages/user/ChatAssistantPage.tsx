import { useState, useRef, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { apiRequest } from '@/shared/api/client';
import { streamSSE } from '@/shared/api/stream';

type Message = { role: 'user' | 'assistant'; content: string };
type Session = { id: string; title: string; created_at: string; updated_at: string };

const suggestions = ['合同违约金上限是多少？', '借贷合同需要哪些必备条款？', '如何认定格式条款的效力？'];

export function ChatAssistantPage() {
  const [searchParams] = useSearchParams();
  const urlSessionId = searchParams.get('session');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '你好！我是法律学习 AI 助手。请问有什么法律问题我可以帮助你解答？' },
  ]);
  const [input, setInput] = useState('');
  const [answering, setAnswering] = useState(false);
  const [sessionReady, setSessionReady] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<boolean>(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load sessions list
  const fetchSessions = useCallback(async () => {
    try {
      const data = await apiRequest<Session[]>('/api/chat/sessions?limit=50');
      setSessions(data);
    } catch {
      // silent
    } finally {
      setSessionsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchSessions();
  }, [fetchSessions]);

  // Auto-load session from URL param on mount
  useEffect(() => {
    if (urlSessionId && !sessionId) {
      setSessionId(urlSessionId);
      loadSession(urlSessionId);
    }
  }, [urlSessionId]);  // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-load session from URL param on mount
  useEffect(() => {
    if (urlSessionId && !sessionId) {
      setSessionId(urlSessionId);
      loadSession(urlSessionId);
    }
  }, [urlSessionId]);  // eslint-disable-line react-hooks/exhaustive-deps

  // Load messages for a session
  const loadSession = useCallback(async (sid: string) => {
    setSessionId(sid);
    setSessionReady(false);
    try {
      const data = await apiRequest<{ id: string; title: string; messages: Array<{ role: string; content: string }> }>(
        `/api/chat/sessions/${sid}`,
      );
      const loaded: Message[] = data.messages.length > 0
        ? data.messages.map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content }))
        : [{ role: 'assistant', content: '你好！我是法律学习 AI 助手。请问有什么法律问题我可以帮助你解答？' }];
      setMessages(loaded);
    } catch {
      setMessages([{ role: 'assistant', content: '加载会话失败，请重试。' }]);
    } finally {
      setSessionReady(true);
    }
  }, []);

  // Create new session
  const createSession = useCallback(async () => {
    setSessionReady(false);
    try {
      const session = await apiRequest<{ id: string; title: string }>('/api/chat/sessions', {
        method: 'POST',
        body: { title: '新对话' },
      });
      setSessionId(session.id);
      setMessages([{ role: 'assistant', content: '你好！我是法律学习 AI 助手。请问有什么法律问题我可以帮助你解答？' }]);
      setSessionReady(true);
      void fetchSessions();
    } catch {
      setSessionReady(true);
    }
  }, [fetchSessions]);

  // Delete a session
  const deleteSession = useCallback(async (sid: string) => {
    setDeleting(sid);
    try {
      await apiRequest(`/api/chat/sessions/${sid}`, { method: 'DELETE' });
      setSessions((prev) => prev.filter((s) => s.id !== sid));
      if (sessionId === sid) {
        // If deleting current session, create a new one
        void createSession();
      }
    } catch {
      // silent
    } finally {
      setDeleting(null);
    }
  }, [sessionId, createSession]);

  // Initial session creation
  useEffect(() => {
    void createSession();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const send = useCallback(async (text: string) => {
    const content = text.trim();
    if (!content || answering) return;

    setMessages((prev) => [...prev, { role: 'user', content }]);
    setInput('');
    setAnswering(true);
    abortRef.current = false;
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

    try {
      if (sessionId) {
        await streamSSE(
          `/api/chat/sessions/${sessionId}/messages/stream`,
          { content },
          (chunk) => {
            if (abortRef.current) return;
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === 'assistant') {
                updated[updated.length - 1] = { ...last, content: last.content + chunk };
              }
              return updated;
            });
          },
        );
      } else {
        await new Promise((r) => setTimeout(r, 800));
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === 'assistant') {
            updated[updated.length - 1] = { ...last, content: '抱歉，会话创建失败。请刷新页面重试。' };
          }
          return updated;
        });
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '请求失败';
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          updated[updated.length - 1] = { ...last, content: `抱歉，发生了错误：${errorMsg}` };
        }
        return updated;
      });
    } finally {
      setAnswering(false);
      void fetchSessions();
    }
  }, [answering, sessionId, fetchSessions]);

  const formatTime = (iso: string) => {
    try {
      return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <PageContainer className="flex h-[calc(100vh-140px)] flex-col space-y-4">
      <div>
        <Badge tone="brand">智能问答</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">法律知识问答</h1>
      </div>

      <div className="flex flex-1 gap-4 overflow-hidden">
        {/* Session sidebar */}
        <div className="hidden w-64 flex-shrink-0 flex-col rounded-2xl border border-slate-200 bg-white lg:flex">
          <div className="border-b border-slate-100 p-3">
            <Button size="sm" className="w-full" onClick={() => void createSession()}>
              + 新对话
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {sessionsLoading ? (
              <div className="space-y-2 p-2">
                <Skeleton className="h-10" />
                <Skeleton className="h-10" />
                <Skeleton className="h-10" />
              </div>
            ) : sessions.length > 0 ? (
              sessions.map((s) => (
                <div
                  key={s.id}
                  className={`group flex items-center justify-between rounded-xl px-3 py-2.5 text-sm cursor-pointer transition ${
                    sessionId === s.id
                      ? 'bg-brand-50 border border-brand-200 text-brand-700'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <div
                    className="min-w-0 flex-1 overflow-hidden"
                    onClick={() => void loadSession(s.id)}
                  >
                    <div className="truncate font-medium">{s.title || '未命名对话'}</div>
                    <div className="mt-0.5 text-xs text-slate-400">{formatTime(s.updated_at)}</div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      void deleteSession(s.id);
                    }}
                    disabled={deleting === s.id}
                    className="ml-1 flex-shrink-0 rounded p-1 text-slate-300 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                    title="删除对话"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-xs text-slate-400">暂无历史对话</div>
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[72%] rounded-2xl px-4 py-3 text-sm leading-7 ${
                    msg.role === 'user'
                      ? 'bg-brand-600 text-white'
                      : 'rounded-tl-sm border border-slate-200 bg-white text-slate-700'
                  }`}
                >
                  {msg.content || (answering && i === messages.length - 1 ? '正在思考...' : '')}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-slate-100 p-4">
            <div className="mb-3 flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  disabled={answering}
                  className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 transition hover:bg-brand-50 hover:border-brand-200 hover:text-brand-700 disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send(input)}
                placeholder="输入法律问题..."
                disabled={!sessionReady}
                className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100 disabled:opacity-50"
              />
              <Button onClick={() => send(input)} loading={answering} disabled={!sessionReady}>
                发送
              </Button>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
