import re

with open(r"D:\homework\frontend\src\pages\user\HistoryPage.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add showExportFor state
content = content.replace(
    "const [deleting, setDeleting] = useState",
    'const [showExportFor, setShowExportFor] = useState<string | null>(null);\n  const [deleting, setDeleting] = useState'
)

# 2. Replace the end of handleDelete to add handleExportHistory
old_end = "    } finally {\n      setDeleting(null);\n    }\n  };"

new_func = '''    } finally {
      setDeleting(null);
    }
  };

  const handleExportHistory = async (item: HistoryItem, format: string) => {
    setShowExportFor(null);
    try {
      let detailUrl = "";
      if (item.type === "analysis") {
        detailUrl = "/api/document/analysis/" + item.id;
      } else if (item.type === "comparison") {
        detailUrl = "/api/document/comparisons/" + item.id;
      } else {
        return;
      }

      const token = localStorage.getItem("legal_ai.access_token");
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = "Bearer " + token;

      const detailResp = await fetch(detailUrl, { headers });
      if (!detailResp.ok) throw new Error("\u83b7\u53d6\u8be6\u60c5\u5931\u8d25");
      const detail = await detailResp.json();

      const body: Record<string, unknown> = {
        document_name: item.title || item.document_a || "\u672a\u77e5\u6587\u6863",
        summary: detail.summary || "",
        risks: detail.risks || detail.changes || [],
        overall_risk_level: detail.overall_risk_level || item.overall_risk_level || null,
        overall_score: detail.overall_score ?? item.overall_score ?? null,
        format,
      };

      const exportHeaders: Record<string, string> = { "Content-Type": "application/json" };
      if (token) exportHeaders["Authorization"] = "Bearer " + token;

      const exportResp = await fetch("/api/document/export", {
        method: "POST",
        headers: exportHeaders,
        body: JSON.stringify(body),
      });

      if (!exportResp.ok) {
        const errData = await exportResp.json().catch(() => null);
        throw new Error(errData?.detail || "\u5bfc\u51fa\u5931\u8d25: " + exportResp.status);
      }

      const blob = await exportResp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const ext = format === "docx" ? ".docx" : format === "pdf" ? ".pdf" : ".txt";
      const docName = item.title || item.document_a || "\u672a\u77e5\u6587\u6863";
      a.download = "\u5206\u6790\u62a5\u544a_" + docName + "_" + Date.now() + ext;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err instanceof Error ? err.message : "\u5bfc\u51fa\u5931\u8d25");
    }
  };'''

content = content.replace(old_end, new_func)

# 3. Replace buttons section
old_buttons = '''                <div className="flex gap-2 shrink-0">
                  <Button variant="ghost" size="sm" onClick={() => navigate(detailPath)}>\u67e5\u770b</Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500"
                    disabled={deleting === item.type + '-' + item.id}
                    onClick={(e) => { e.stopPropagation(); handleDelete(item); }}
                  >
                    {deleting === item.type + '-' + item.id ? '\u5220\u9664\u4e2d...' : '\u5220\u9664'}
                  </Button>
                </div>'''

new_buttons = '''                <div className="flex gap-2 shrink-0">
                  <Button variant="ghost" size="sm" onClick={() => navigate(detailPath)}>\u67e5\u770b</Button>
                  {item.type !== 'chat' && (
                    <div className="relative">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); setShowExportFor(showExportFor === item.type + '-' + item.id ? null : item.type + '-' + item.id); }}
                      >
                        \u5bfc\u51fa \u25be
                      </Button>
                      {showExportFor === item.type + '-' + item.id && (
                        <div className="absolute right-0 mt-1 w-32 rounded-xl border border-slate-200 bg-white shadow-lg z-50 py-1">
                          <button
                            className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"
                            onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'docx'); }}
                          >
                            \U0001F4C4 Word
                          </button>
                          <button
                            className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"
                            onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'pdf'); }}
                          >
                            \U0001F4D1 PDF
                          </button>
                          <button
                            className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"
                            onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'txt'); }}
                          >
                            \U0001F4DD TXT
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500"
                    disabled={deleting === item.type + '-' + item.id}
                    onClick={(e) => { e.stopPropagation(); handleDelete(item); }}
                  >
                    {deleting === item.type + '-' + item.id ? '\u5220\u9664\u4e2d...' : '\u5220\u9664'}
                  </Button>
                </div>'''

count = content.count(old_buttons)
print(f"Found {count} button patterns")

if count > 0:
    content = content.replace(old_buttons, new_buttons)
    print("Buttons replaced")
else:
    print("ERROR: pattern not found, trying fuzzy match")
    if "\u67e5\u770b" in content:
        idx = content.find("\u67e5\u770b")
        print(f"Area: {content[idx-80:idx+80]}")

with open(r"D:\homework\frontend\src\pages\user\HistoryPage.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")