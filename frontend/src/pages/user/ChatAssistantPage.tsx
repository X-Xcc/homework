import { useState, useRef, useEffect } from 'react';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';

type Message = { role: 'user' | 'assistant'; content: string };

const suggestions = ['合同违约金上限是多少？', '借款合同需要哪些必备条款？', '如何认定格式条款的效力？'];

export function ChatAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '你好！我是法律学习 AI 助手。请问有什么法律问题我可以帮助你解答？' },
  ]);
  const [input, setInput] = useState('');
  const [answering, setAnswering] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = (text: string) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setAnswering(true);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `根据相关法律规定，${text} 涉及以下要点：首先，需要明确合同的主体资格和标的物。其次，应当审查合同的形式要件和实质要件是否完备。最后，建议咨询专业律师进行最终确认。` },
      ]);
      setAnswering(false);
    }, 1800);
  };

  return (
    <PageContainer className="flex h-[calc(100vh-140px)] flex-col space-y-4">
      <div>
        <Badge tone="brand">智能问答</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">法律知识问答</h1>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden">
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
                {msg.content}
              </div>
            </div>
          ))}
          {answering && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-400">
                正在思考...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-slate-100 p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 transition hover:bg-brand-50 hover:border-brand-200 hover:text-brand-700"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send(input)}
              placeholder="输入法律问题..."
              className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
            />
            <Button onClick={() => send(input)} loading={answering}>
              发送
            </Button>
          </div>
        </div>
      </Card>
    </PageContainer>
  );
}
