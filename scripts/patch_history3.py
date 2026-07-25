with open(r"D:\homework\frontend\src\pages\user\HistoryPage.tsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # 1. Add showExportFor state
    if "const [deleting, setDeleting] = useState" in line:
        new_lines.append(line)
        new_lines.append("  const [showExportFor, setShowExportFor] = useState<string | null>(null);\n")
        i += 1
        continue

    # 2. After handleDelete closing, insert handleExportHistory
    if line.rstrip() == "  };" and i > 0 and "setDeleting(null);" in lines[i-1]:
        new_lines.append(line)
        new_lines.append("\n")
        func_body = [
            "  const handleExportHistory = async (item: HistoryItem, format: string) => {",
            "    setShowExportFor(null);",
            "    try {",
            '      let detailUrl = "";',
            '      if (item.type === "analysis") {',
            '        detailUrl = "/api/document/analysis/" + item.id;',
            '      } else if (item.type === "comparison") {',
            '        detailUrl = "/api/document/comparisons/" + item.id;',
            "      } else {",
            "        return;",
            "      }",
            "",
            '      const token = localStorage.getItem("legal_ai.access_token");',
            "      const headers: Record<string, string> = {};",
            '      if (token) headers["Authorization"] = "Bearer " + token;',
            "",
            "      const detailResp = await fetch(detailUrl, { headers });",
            '      if (!detailResp.ok) throw new Error("\u83b7\u53d6\u8be6\u60c5\u5931\u8d25");',
            "      const detail = await detailResp.json();",
            "",
            "      const body: Record<string, unknown> = {",
            '        document_name: item.title || item.document_a || "\u672a\u77e5\u6587\u6863",',
            '        summary: detail.summary || "",',
            "        risks: detail.risks || detail.changes || [],",
            "        overall_risk_level: detail.overall_risk_level || item.overall_risk_level || null,",
            "        overall_score: detail.overall_score ?? item.overall_score ?? null,",
            "        format,",
            "      };",
            "",
            '      const exportHeaders: Record<string, string> = { "Content-Type": "application/json" };',
            '      if (token) exportHeaders["Authorization"] = "Bearer " + token;',
            "",
            '      const exportResp = await fetch("/api/document/export", {',
            '        method: "POST",',
            "        headers: exportHeaders,",
            "        body: JSON.stringify(body),",
            "      });",
            "",
            "      if (!exportResp.ok) {",
            "        const errData = await exportResp.json().catch(() => null);",
            '        throw new Error(errData?.detail || "\u5bfc\u51fa\u5931\u8d25: " + exportResp.status);',
            "      }",
            "",
            "      const blob = await exportResp.blob();",
            "      const url = URL.createObjectURL(blob);",
            '      const a = document.createElement("a");',
            "      a.href = url;",
            '      const ext = format === "docx" ? ".docx" : format === "pdf" ? ".pdf" : ".txt";',
            '      const docName = item.title || item.document_a || "\u672a\u77e5\u6587\u6863";',
            '      a.download = "\u5206\u6790\u62a5\u544a_" + docName + "_" + Date.now() + ext;',
            "      a.click();",
            "      URL.revokeObjectURL(url);",
            "    } catch (err) {",
            '      alert(err instanceof Error ? err.message : "\u5bfc\u51fa\u5931\u8d25");',
            "    }",
            "  };",
        ]
        for s in func_body:
            new_lines.append(s + "\n")
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(r"D:\homework\frontend\src\pages\user\HistoryPage.tsx", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Done! {len(new_lines)} lines")
