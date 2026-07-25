import { Outlet } from 'react-router-dom';

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50 to-white px-4 py-10">
      <div className="w-full max-w-5xl overflow-hidden rounded-[32px] border border-white/70 bg-white/90 shadow-2xl shadow-slate-200/70 backdrop-blur">
        <div className="grid min-h-[680px] lg:grid-cols-[1.1fr_0.9fr]">
          <div className="hidden bg-slate-950 px-10 py-12 text-white lg:flex lg:flex-col lg:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-indigo-300">Legal AI Workspace</div>
              <h1 className="mt-4 text-4xl font-semibold leading-tight">法律学习 AI 工作台</h1>
              <p className="mt-4 max-w-md text-sm leading-7 text-slate-300">
                面向法学生与法律从业者的智能工作区，串联合同分析、法条检索、知识沉淀与后台治理。
              </p>
            </div>
            <div className="space-y-4">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <div className="text-sm font-medium text-indigo-200">当前交付重点</div>
                <p className="mt-2 text-sm leading-7 text-slate-300">先打通前台工作区与后台管理端骨架，再逐步接入真实鉴权与业务接口。</p>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="text-indigo-200">前台</div>
                  <div className="mt-1 text-slate-100">分析 / 对比 / 检索 / 问答</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="text-indigo-200">后台</div>
                  <div className="mt-1 text-slate-100">用户 / 模板 / 日志 / 配置</div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-center px-6 py-10 sm:px-10 lg:px-12">
            <div className="w-full max-w-md">
              <Outlet />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
