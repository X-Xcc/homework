import { useState, useRef } from 'react';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';

const mockRisks = [
  { level: '高', clause: '第十条 · 违约责任', content: '未约定违约金金额，仅规定"依法承担违约责任"，实际执行存在不确定性。', advice: '建议明确违约金数额或计算方式。' },
  { level: '中', clause: '第七条 · 保密条款', content: '保密期限未作限定，效力可能延伸至合同终止后无限期。', advice: '建议约定明确的保密期限（如 2-3 年）。' },
  { level: '低', clause: '第十二条 · 争议解决', content: '未指定争议解决机构，发生纠纷时需协商选择。', advice: '建议补充仲裁条款或指定管辖法院。' },
];

export function ContractAnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setAnalyzed(false);
    }
  };

  const handleAnalyze = () => {
    if (!file) return;
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      setAnalyzed(true);
    }, 2500);
  };

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">合同分析</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">合同风险分析</h1>
        <p className="mt-1 text-sm text-slate-500">上传合同文档，AI 自动识别风险条款并给出修改建议。</p>
      </div>

      {!analyzed ? (
        <Card className="space-y-4">
          <Panel title="上传合同" description="支持 PDF、Word、图片（OCR）格式">
            <div
              className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-10 transition hover:border-brand-200 hover:bg-brand-50/30"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
                className="hidden"
                onChange={handleFileChange}
              />
              <div className="text-5xl text-slate-300">📄</div>
              <div className="mt-4 text-sm font-medium text-slate-500">
                {file ? file.name : '点击上传或拖拽文件到这里'}
              </div>
              <div className="mt-2 text-xs text-slate-400">支持 PDF / Word / 图片（jpg, png）</div>
              {file && (
                <Button className="mt-4" onClick={(e) => { e.stopPropagation(); handleAnalyze(); }} loading={analyzing}>
                  开始分析
                </Button>
              )}
            </div>
          </Panel>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Badge tone="success">分析完成</Badge>
              <span className="ml-2 text-sm text-slate-500">{file?.name}</span>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" onClick={() => { setAnalyzed(false); setFile(null); }}>重新上传</Button>
              <Button>导出报告</Button>
            </div>
          </div>
          {mockRisks.map((risk) => (
            <Card key={risk.clause}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Badge tone={risk.level === '高' ? 'warning' : risk.level === '中' ? 'brand' : 'neutral'}>{risk.level}风险</Badge>
                    <span className="text-sm font-medium text-slate-700">{risk.clause}</span>
                  </div>
                  <p className="mt-2 text-sm leading-7 text-slate-600">{risk.content}</p>
                  <p className="mt-2 text-sm font-medium text-brand-600">💡 {risk.advice}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </PageContainer>
  );
}
