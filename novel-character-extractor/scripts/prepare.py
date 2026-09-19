# -*- coding: utf-8 -*-
"""把原著(epub/txt/文件夹)转成干净的 UTF-8 纯文本，每卷一个 txt。

用法: python prepare.py <原著路径> [输出目录]     # 输出目录默认 _charwork/src
处理: epub 按 spine 顺序抽纯文本；txt 自动猜编码(utf-8-sig→gb18030→big5→utf-16，
      全部失败则 utf-8 容错解码，坏字节替换)。
注意: 跑完后必须抽查一两个输出文件开头，确认不是乱码再继续后续步骤。
"""
import sys, os, re, html, zipfile
from pathlib import Path

def strip_html(raw: str) -> str:
    raw = re.sub(r'(?is)<(script|style).*?</\1>', '', raw)
    raw = re.sub(r'(?i)<(br\s*/?|/p|/div|/h[1-6]|/li|/tr)[^>]*>', '\n', raw)
    raw = re.sub(r'(?i)<h([1-6])[^>]*>', lambda m: '\n' + '#' * int(m.group(1)) + ' ', raw)
    raw = re.sub(r'(?i)<p[^>]*>', '\n', raw)
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = html.unescape(raw).replace('\u3000', ' ')
    raw = re.sub(r'[ \t]+', ' ', raw)
    raw = re.sub(r'\n\s*\n+', '\n\n', raw)
    return raw.strip()

def decode_txt(data: bytes):
    for enc in ('utf-8-sig', 'gb18030', 'big5', 'utf-16'):
        try:
            return data.decode(enc), enc
        except Exception:
            continue
    return data.decode('utf-8', 'replace'), 'utf-8/replace'

def epub_to_text(p: Path) -> str:
    parts = []
    with zipfile.ZipFile(p) as z:
        items = [i for i in z.namelist() if re.search(r'\.(x?html?|htm)$', i, re.I)]
        spine = []
        opfs = [i for i in z.namelist() if i.endswith('.opf')]
        if opfs:
            try:
                d = z.read(opfs[0]).decode('utf-8', 'ignore')
                idmap = dict(re.findall(r'<item[^>]*id="([^"]+)"[^>]*href="([^"]+)"', d))
                base = os.path.dirname(opfs[0])
                for idref in re.findall(r'<itemref[^>]*idref="([^"]+)"', d):
                    href = idmap.get(idref)
                    if href:
                        q = os.path.normpath((base + '/' + href) if base else href).replace('\\', '/')
                        spine.append(q)
            except Exception:
                pass
        ordered = [s for s in spine if s in items] or sorted(items)
        for it in ordered:
            try:
                t = strip_html(z.read(it).decode('utf-8', 'ignore'))
            except Exception:
                continue
            if t:
                parts.append(t)
    return '\n\n'.join(parts)

def main():
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2] if len(sys.argv) > 2 else '_charwork/src')
    out.mkdir(parents=True, exist_ok=True)
    files = [src] if src.is_file() else sorted(p for p in src.rglob('*') if p.suffix.lower() in ('.epub', '.txt'))
    if not files:
        print('未找到 epub/txt 文件:', src); sys.exit(1)
    for p in files:
        dest = out / (p.stem + '.txt')
        if dest.exists():
            print(f'[skip] {dest.name}'); continue
        if p.suffix.lower() == '.epub':
            text = epub_to_text(p); enc = 'epub'
        else:
            text, enc = decode_txt(p.read_bytes())
        dest.write_text(text, encoding='utf-8')
        print(f'{dest.name}: {len(text)} chars ({enc})')

if __name__ == '__main__':
    main()
