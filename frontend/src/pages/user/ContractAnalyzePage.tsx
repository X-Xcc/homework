import { useState, useRef } from 'react';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { EmptyState } from '@/shared/ui/EmptyState';

type RiskItem = {
  id?: string;
  level: string;
  title: string;
  description: string;
  location?: string | null;
  legal_basis?: string[];
  suggestion?: string | null;
};

type AnalyzeResult = {
  id: string;
  document_name: string;
  status: string;
  risks: RiskItem[];
  summary?: string | null;
  overall_risk_level?: string;
  overall_score?: number;
};

function RiskLevelBadge({ level }: { level: string }) {
  const tone = level === 'high' ? 'warning' : level === 'medium' ? 'brand' : 'neutral';
  const label = level === 'high' ? '高风险' : level === 'medium' ? '中风险' : '低风险';
  return <Badge tone={tone}>{label}</Badge>;
}

export function ContractAnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    setResult(null);
    setStreamingText('');
    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('legal_ai.access_token');
      const headers: Record<string, string> = { Accept: 'text/event-stream' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch('/api/document/analyze/stream', {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `请求失败: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('无法读取流式响应');

      const decoder = new TextDecoder();
      let buffer = '';
      let finalResult: AnalyzeResult | null = null;
      let progressText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data: ')) continue;
          const data = trimmed.slice(6);
          if (data === '[DONE]') continue;
          try {
            const parsed = JSON.parse(data);
            if (parsed.content) {
              progressText += parsed.content;
              setStreamingText(progressText);
            }
            if (parsed.result) {
              finalResult = parsed.result as AnalyzeResult;
            }
          } catch {
            // skip non-JSON
          }
        }
      }

      if (finalResult) {
        setResult(finalResult);
      } else {
        // Fallback: try to parse accumulated text as JSON
        try {
          const parsed = JSON.parse(progressText);
          setResult({
            id: parsed.id ?? '',
            document_name: file.name,
            status: 'completed',
            risks: parsed.risks ?? [],
            summary: parsed.summary ?? progressText,
            overall_risk_level: parsed.overall_risk_level,
            overall_score: parsed.overall_score,
          });
        } catch {
          setResult({
            id: '',
            document_name: file.name,
            status: 'completed',
            risks: [],
            summary: progressText,
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败');
    } finally {
      setAnalyzing(false);
      setStreamingText('');
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setStreamingText('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleExport = async (format: string) => {
    if (!result) return;
    try {
      const token = localStorage.getItem('legal_ai.access_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const body = {
        document_name: result.document_name,
        summary: result.summary || '',
        risks: result.risks,
        overall_risk_level: result.overall_risk_level || null,
        overall_score: result.overall_score ?? null,
        format,
      };

      const response = await fetch('/api/document/export', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `导出失败: ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const ext = format === 'docx' ? '.docx' : format === 'pdf' ? '.pdf' : '.txt';
      a.download = `分析报告_${result.document_name || '未知文档'}_${Date.now()}${ext}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err instanceof Error ? err.message : '导出失败');
    }
  };

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">合同分析</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">合同风险分析</h1>
        <p className="mt-1 text-sm text-slate-500">上传合同文档，AI 自动识别风险条款并给出修改建议。</p>
      </div>

      {!result ? (
        <Card className="space-y-4">
          <Panel title="上传合同" description="支持 PDF、Word、图片（OCR）格式">
            <div
              className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-10 transition hover:border-brand-200 hover:bg-brand-50/30 cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png"
                className="hidden"
                onChange={handleFileChange}
              />
              <div className="text-5xl text-slate-300">📁</div>
              <div className="mt-4 text-sm font-medium text-slate-500">
                {file ? file.name : '点击上传或拖拽文件到这里'}
              </div>
              <div className="mt-2 text-xs text-slate-400">支持 PDF / Word / 图片（jpg, png）</div>
              {file && (
                <Button
                  className="mt-4"
                  onClick={(e) => { e.stopPropagation(); handleAnalyze(); }}
                  loading={analyzing}
                >
                  开始分析
                </Button>
              )}
            </div>
          </Panel>
          {analyzing && (
            <Card className="space-y-3">
              {streamingText ? (
                <div className="text-sm leading-7 text-slate-600 whitespace-pre-wrap">
                  {streamingText}
                  <span className="inline-block w-2 h-4 bg-brand-600 animate-pulse ml-0.5 align-text-bottom" />
                </div>
              ) : (
                <>
                  <Skeleton className="h-16" />
                  <Skeleton className="h-16" />
                  <Skeleton className="h-16" />
                </>
              )}
            </Card>
          )}
          {error && <EmptyState title="分析失败" description={error} />}
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Badge tone="success">分析完成</Badge>
              <span className="text-sm text-slate-500">{result.document_name}</span>
              {result.overall_risk_level && <RiskLevelBadge level={result.overall_risk_level} />}
              {result.overall_score != null && (
                <span className="text-sm font-semibold text-brand-600">评分 {result.overall_score}</span>
              )}
            </div>
            <div className="flex gap-3">
                          <div className="relative">
              <Button variant="secondary" onClick={() => setShowExportMenu(!showExportMenu)}>导出报告 ▾</Button>
              {showExportMenu && (
                <div className="absolute right-0 mt-1 w-36 rounded-xl border border-slate-200 bg-white shadow-lg z-50 py-1">
                  <button
                    className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50 transition"
                    onClick={() => { handleExport('docx'); setShowExportMenu(false); }}
                  >
                    📄 Word 格式
                  </button>
                  <button
                    className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50 transition"
                    onClick={() => { handleExport('pdf'); setShowExportMenu(false); }}
                  >
                    📑 PDF 格式
                  </button>
                  <button
                    className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50 transition"
                    onClick={() => { handleExport('txt'); setShowExportMenu(false); }}
                  >
                    📝 TXT 格式
                  </button>
                </div>
              )}
            </div>
              <Button variant="secondary" onClick={handleReset}>重新上传</Button>
            </div>
          </div>

          {result.summary && (
            <Card>
              <div className="text-sm font-semibold text-slate-900 mb-2">分析总结</div>
              <p className="text-sm leading-7 text-slate-600">{result.summary}</p>
            </Card>
          )}

          {result.risks.length > 0 ? (
            result.risks.map((risk, i) => (
              <Card key={risk.id || i}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <RiskLevelBadge level={risk.level} />
                      <span className="text-sm font-medium text-slate-700">{risk.title}</span>
                      {risk.location && (
                        <span className="text-xs text-slate-400">· {risk.location}</span>
                      )}
                    </div>
                    <p className="mt-2 text-sm leading-7 text-slate-600">{risk.description}</p>
                    {risk.legal_basis && risk.legal_basis.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {risk.legal_basis.map((basis, j) => (
                          <Badge key={j} tone="neutral" className="text-xs">{basis}</Badge>
                        ))}
                      </div>
                    )}
                    {risk.suggestion && (
                      <p className="mt-2 text-sm font-medium text-brand-600">💡 {risk.suggestion}</p>
                    )}
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <EmptyState title="未发现风险" description="该文档未检测到明显风险条款。" />
          )}
        </div>
      )}
    </PageContainer>
  );
}


