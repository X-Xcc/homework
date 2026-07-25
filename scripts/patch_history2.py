with open(r"D:\homework\frontend\src\pages\user\HistoryPage.tsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Build new file with modifications
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # 1. Add showExportFor state after deleting state
    if "const [deleting, setDeleting] = useState" in line:
        new_lines.append(line)
        new_lines.append("  const [showExportFor, setShowExportFor] = useState<string | null>(null);\n")
        i += 1
        continue

    # 2. After handleDelete closing, insert handleExportHistory
    if line.rstrip() == "  };" and i > 0 and "setDeleting(null);" in lines[i-1]:
        new_lines.append(line)
        new_lines.append("\n")
        new_lines.append("  const handleExportHistory = async (item: HistoryItem, format: string) => {\n")
        new_lines.append("    setShowExportFor(null);\n")
        new_lines.append("    try {\n")
        new_lines.append('      let detailUrl = "";\n')
        new_lines.append('      if (item.type === "analysis") {\n')
        new_lines.append('        detailUrl = "/api/document/analysis/" + item.id;\n')
        new_lines.append('      } else if (item.type === "comparison") {\n')
        new_lines.append('        detailUrl = "/api/document/comparisons/" + item.id;\n')
        new_lines.append("      } else {\n")
        new_lines.append("        return;\n")
        new_lines.append("      }\n")
        new_lines.append("\n")
        new_lines.append('      const token = localStorage.getItem("legal_ai.access_token");\n')
        new_lines.append("      const headers: Record<string, string> = {};\n")
        new_lines.append('      if (token) headers["Authorization"] = "Bearer " + token;\n')
        new_lines.append("\n")
        new_lines.append("      const detailResp = await fetch(detailUrl, { headers });\n")
        new_lines.append('      if (!detailResp.ok) throw new Error("\u83b7\u53d6\u8be6\u60c5\u5931\u8d25");\n')
        new_lines.append("      const detail = await detailResp.json();\n")
        new_lines.append("\n")
        new_lines.append("      const body: Record<string, unknown> = {\n")
        new_lines.append('        document_name: item.title || item.document_a || "\u672a\u77e5\u6587\u6863",\n')
        new_lines.append('        summary: detail.summary || "",\n')
        new_lines.append("        risks: detail.risks || detail.changes || [],\n")
        new_lines.append("        overall_risk_level: detail.overall_risk_level || item.overall_risk_level || null,\n")
        new_lines.append("        overall_score: detail.overall_score ?? item.overall_score ?? null,\n")
        new_lines.append("        format,\n")
        new_lines.append("      };\n")
        new_lines.append("\n")
        new_lines.append('      const exportHeaders: Record<string, string> = { "Content-Type": "application/json" };\n')
        new_lines.append('      if (token) exportHeaders["Authorization"] = "Bearer " + token;\n')
        new_lines.append("\n")
        new_lines.append('      const exportResp = await fetch("/api/document/export", {\n')
        new_lines.append('        method: "POST",\n')
        new_lines.append("        headers: exportHeaders,\n")
        new_lines.append("        body: JSON.stringify(body),\n")
        new_lines.append("      });\n")
        new_lines.append("\n")
        new_lines.append("      if (!exportResp.ok) {\n")
        new_lines.append("        const errData = await exportResp.json().catch(() => null);\n")
        new_lines.append('        throw new Error(errData?.detail || "\u5bfc\u51fa\u5931\u8d25: " + exportResp.status);\n')
        new_lines.append("      }\n")
        new_lines.append("\n")
        new_lines.append("      const blob = await exportResp.blob();\n")
        new_lines.append("      const url = URL.createObjectURL(blob);\n")
        new_lines.append('      const a = document.createElement("a");\n')
        new_lines.append("      a.href = url;\n")
        new_lines.append('      const ext = format === "docx" ? ".docx" : format === "pdf" ? ".pdf" : ".txt";\n')
        new_lines.append('      const docName = item.title || item.document_a || "\u672a\u77e5\u6587\u6863";\n')
        new_lines.append('      a.download = "\u5206\u6790\u62a5\u544a_" + docName + "_" + Date.now() + ext;\n')
        new_lines.append("      a.click();\n")
        new_lines.append("      URL.revokeObjectURL(url);\n")
        new_lines.append("    } catch (err) {\n")
        new_lines.append('      alert(err instanceof Error ? err.message : "\u5bfc\u51fa\u5931\u8d25");\n')
        new_lines.append("    }\n")
        new_lines.append("  };\n")
        i += 1
        continue

    # 3. In the button row, add export dropdown before delete button
    if '<Button variant="ghost" size="sm" onClick={() => navigate(detailPath)}>\u67e5\u770b</Button>' in line:
        new_lines.append(line)  # Keep the view button line
        # Insert export dropdown on next line
        indent = "                  "
        new_lines.append(indent + "{item.type !== 'chat' && (\n")
        new_lines.append(indent + '  <div className="relative">\n')
        new_lines.append(indent + "    <Button\n")
        new_lines.append(indent + '      variant="ghost"\n')
        new_lines.append(indent + '      size="sm"\n')
        new_lines.append(indent + "      onClick={(e) => { e.stopPropagation(); setShowExportFor(showExportFor === item.type + '-' + item.id ? null : item.type + '-' + item.id); }}\n")
        new_lines.append(indent + "    >\n")
        new_lines.append(indent + '      \u5bfc\u51fa \u25be\n')
        new_lines.append(indent + "    </Button>\n")
        new_lines.append(indent + "    {showExportFor === item.type + '-' + item.id && (\n")
        new_lines.append(indent + '      <div className="absolute right-0 mt-1 w-32 rounded-xl border border-slate-200 bg-white shadow-lg z-50 py-1">\n')
        new_lines.append(indent + "        <button\n")
        new_lines.append(indent + '          className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"\n')
        new_lines.append(indent + "          onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'docx'); }}\n")
        new_lines.append(indent + "        >\n")
        new_lines.append(indent + "          \U0001F4C4 Word\n")
        new_lines.append(indent + "        </button>\n")
        new_lines.append(indent + "        <button\n")
        new_lines.append(indent + '          className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"\n')
        new_lines.append(indent + "          onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'pdf'); }}\n")
        new_lines.append(indent + "        >\n")
        new_lines.append(indent + "          \U0001F4D1 PDF\n")
        new_lines.append(indent + "        </button>\n")
        new_lines.append(indent + "        <button\n")
        new_lines.append(indent + '          className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"\n')
        new_lines.append(indent + "          onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'txt'); }}\n")
        new_lines.append(indent + "        >\n")
        new_lines.append(indent + "          \U0001F4DD TXT\n")
        new_lines.append(indent + "        </button>\n")
        new_lines.append(indent + "      </div>\n")
        new_lines.append(indent + "    )}\n")
        new_lines.append(indent + "  </div>\n")
        new_lines.append(indent + ")}\n")
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(r"D:\homework\frontend\src\pages\user\HistoryPage.tsx", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Done! Lines written:", len(new_lines))