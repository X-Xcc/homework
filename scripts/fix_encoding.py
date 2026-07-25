import re

with open(r"D:\homework\backend\app\api\document.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the filename encoding issue - use RFC 5987 encoding
old_lines = '''    filename = f"分析报告_{req.document_name or '未知文档'}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"

    return Response(
        content=buf.getvalue(),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )'''

new_lines = '''    from urllib.parse import quote
    raw_filename = f"分析报告_{req.document_name or '未知文档'}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    safe_filename = quote(raw_filename)
    content_disposition = f"attachment; filename*=UTF-8''{safe_filename}"

    return Response(
        content=buf.getvalue(),
        media_type=media_type,
        headers={"Content-Disposition": content_disposition}
    )'''

if old_lines in content:
    content = content.replace(old_lines, new_lines)
    print("Replaced successfully")
else:
    print("Pattern not found - trying to locate")
    idx = content.find('filename = f"')
    if idx >= 0:
        print(f"Found at {idx}: {repr(content[idx:idx+100])}")
    else:
        print("Not found at all")

with open(r"D:\homework\backend\app\api\document.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done")